import os
import re
import shutil
from typing import Dict, Any, Optional
import yt_dlp
import imageio_ffmpeg

def get_ffmpeg_executable() -> str:
    """
    Obtém o caminho do executável do FFmpeg compatível tanto com Windows quanto Linux/Cloud.
    """
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    if os.name != 'nt':
        return ffmpeg_exe

    ffmpeg_dir = os.path.dirname(ffmpeg_exe)
    target_ffmpeg = os.path.join(ffmpeg_dir, 'ffmpeg.exe')
    
    if not os.path.exists(target_ffmpeg):
        try:
            shutil.copyfile(ffmpeg_exe, target_ffmpeg)
        except Exception:
            return ffmpeg_exe
            
    return target_ffmpeg

def sanitize_filename(name: str) -> str:
    """Remove caracteres inválidos para nomes de arquivos no Windows"""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def get_video_info(url: str) -> Dict[str, Any]:
    """
    Obtém metadados do vídeo do YouTube rapidamente sem fazer download.
    """
    ffmpeg_path = get_ffmpeg_executable()
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'ffmpeg_location': ffmpeg_path,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'mweb']
            }
        }
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        return {
            "id": info.get("id", ""),
            "title": info.get("title", "Sem título"),
            "duration": info.get("duration", 0),
            "thumbnail": info.get("thumbnail", ""),
            "channel": info.get("uploader", info.get("channel", "Canal desconhecido")),
            "view_count": info.get("view_count", 0),
            "webpage_url": info.get("webpage_url", url)
        }

def download_video(url: str, output_dir: str = "downloads", video_id: Optional[str] = None) -> str:
    """
    Baixa o vídeo completo em formato MP4 para permitir cortes rápidos.
    Utiliza múltiplos canais de extração (Android + MWeb) para garantir download contínuo no Streamlit Cloud.
    Retorna o caminho do arquivo baixado.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    ffmpeg_path = get_ffmpeg_executable()
    out_template = os.path.join(output_dir, f"{video_id or '%(id)s'}.%(ext)s")
    
    ydl_opts = {
        'format': 'best/bestvideo+bestaudio',
        'outtmpl': out_template,
        'merge_output_format': 'mp4',
        'ffmpeg_location': ffmpeg_path,
        'quiet': False,
        'no_warnings': True,
        'overwrites': False,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'retries': 10,
        'fragment_retries': 10,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'mweb']
            }
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            base, _ = os.path.splitext(filename)
            mp4_filename = f"{base}.mp4"
            if os.path.exists(mp4_filename):
                return mp4_filename
            if os.path.exists(filename):
                return filename
    except Exception as e:
        # Fallback de emergência com stream direto progressivo
        fallback_opts = {
            'format': '18/22/best',
            'outtmpl': out_template,
            'ffmpeg_location': ffmpeg_path,
            'quiet': False,
            'no_warnings': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'retries': 10,
            'fragment_retries': 10,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android']
                }
            }
        }
        with yt_dlp.YoutubeDL(fallback_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            base, _ = os.path.splitext(filename)
            mp4_filename = f"{base}.mp4"
            if os.path.exists(mp4_filename):
                return mp4_filename
            return filename
