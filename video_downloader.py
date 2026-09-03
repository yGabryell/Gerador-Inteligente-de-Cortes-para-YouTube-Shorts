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

def convert_and_save_cookies(raw_data: str, target_path: str = "cookies.txt") -> bool:
    """
    Salva cookies para uso no yt-dlp.
    Suporta formato Netscape (texto tabular clássico) ou formato JSON (Cookie-Editor / EditThisCookie).
    """
    import json
    if not raw_data or not raw_data.strip():
        return False
        
    clean = raw_data.strip()
    
    # Se for formato JSON (ex: exportado por Cookie-Editor como JSON)
    if clean.startswith("[") or clean.startswith("{"):
        try:
            parsed = json.loads(clean)
            if isinstance(parsed, dict):
                parsed = [parsed]
            if isinstance(parsed, list):
                lines = ["# Netscape HTTP Cookie File"]
                for c in parsed:
                    domain = c.get("domain", ".youtube.com")
                    flag = "TRUE" if domain.startswith(".") else "FALSE"
                    path = c.get("path", "/")
                    secure = "TRUE" if c.get("secure", False) else "FALSE"
                    exp = str(int(c.get("expirationDate", 2147483647)))
                    name = c.get("name", "")
                    val = c.get("value", "")
                    if name:
                        lines.append(f"{domain}\t{flag}\t{path}\t{secure}\t{exp}\t{name}\t{val}")
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines) + "\n")
                return True
        except Exception:
            pass

    # Formato Netscape padrão
    with open(target_path, "w", encoding="utf-8") as f:
        if not clean.startswith("#"):
            f.write("# Netscape HTTP Cookie File\n" + clean + "\n")
        else:
            f.write(clean + "\n")
    return True

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
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        },
        'extractor_args': {
            'youtube': {
                'player_client': ['android_creator', 'ios', 'android', 'web_creator']
            }
        }
    }
    
    if os.path.exists("cookies.txt"):
        ydl_opts['cookiefile'] = "cookies.txt"
    elif os.getenv("YOUTUBE_COOKIES"):
        cookie_path = "cookies.txt"
        with open(cookie_path, "w", encoding="utf-8") as f:
            f.write(os.getenv("YOUTUBE_COOKIES"))
        ydl_opts['cookiefile'] = cookie_path
    
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
    Baixa o vídeo completo contornando bloqueios 403 em ambientes de Cloud (Streamlit Cloud).
    """
    os.makedirs(output_dir, exist_ok=True)
    
    ffmpeg_path = get_ffmpeg_executable()
    out_template = os.path.join(output_dir, f"{video_id or '%(id)s'}.%(ext)s")
    
    cookie_file = None
    if os.path.exists("cookies.txt"):
        cookie_file = "cookies.txt"
    elif os.getenv("YOUTUBE_COOKIES"):
        cookie_file = "cookies.txt"
        with open(cookie_file, "w", encoding="utf-8") as f:
            f.write(os.getenv("YOUTUBE_COOKIES"))

    ydl_opts = {
        # Formato flexível com suporte a vídeo separado ou combinado (18, 22, mp4)
        'format': 'bestvideo*+bestaudio/best[ext=mp4]/18/22/b/best',
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
        # Cabeçalhos para simular requisição legítima
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        },
        # Clientes móveis que contornam 403 e oferecem formatos diretos
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web_creator']
            }
        }
    }
    
    if cookie_file:
        ydl_opts['cookiefile'] = cookie_file
    
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
        # Fallback usando formato direto 18/22 via cliente Android
        fallback_opts = {
            'format': '18/22/b/best',
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
        if cookie_file:
            fallback_opts['cookiefile'] = cookie_file
            
        with yt_dlp.YoutubeDL(fallback_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            base, _ = os.path.splitext(filename)
            mp4_filename = f"{base}.mp4"
            if os.path.exists(mp4_filename):
                return mp4_filename
            return filename
