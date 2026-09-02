import re
from typing import List, Dict, Optional, Tuple, Any
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

def extract_video_id(url: str) -> Optional[str]:
    """
    Extrai o ID do vídeo a partir de vários formatos de URL do YouTube:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/live/VIDEO_ID
    - https://www.youtube.com/shorts/VIDEO_ID
    - VIDEO_ID diretamente
    """
    if not url:
        return None
    
    url = url.strip()
    
    # Se já for um ID de 11 caracteres alfanuméricos/hífens
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url
        
    patterns = [
        r'(?:v=|\/v\/|youtu\.be\/|\/embed\/|\/live\/|\/shorts\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
            
    return None

def format_timestamp(seconds: float) -> str:
    """Converte segundos para formato [HH:MM:SS] ou [MM:SS]"""
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def get_transcript_via_ytdlp(video_id: str, preferred_languages: Optional[List[str]] = None) -> Tuple[List[Dict[str, Any]], str]:
    """
    Fallback robusto usando yt-dlp para extrair legendas (manuais e automáticas)
    em formato json3 ou vtt diretamente do YouTube, sem sofrer timeout de conexão.
    """
    import yt_dlp
    import requests

    if preferred_languages is None:
        preferred_languages = ['pt', 'pt-BR', 'pt-PT', 'en', 'es']

    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 15,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        subtitles = info.get('subtitles') or {}
        auto_subtitles = info.get('automatic_captions') or {}

        # 1. Procura nas legendas manuais
        target_sub = None
        for lang in preferred_languages:
            if lang in subtitles:
                target_sub = subtitles[lang]
                break
        
        # 2. Se não achar manual, procura nas automáticas
        if not target_sub:
            for lang in preferred_languages:
                if lang in auto_subtitles:
                    target_sub = auto_subtitles[lang]
                    break

        # 3. Se ainda não achar, pega a primeira disponível
        if not target_sub:
            if subtitles:
                target_sub = list(subtitles.values())[0]
            elif auto_subtitles:
                target_sub = list(auto_subtitles.values())[0]

        if not target_sub:
            raise NoTranscriptFound("Não foram encontradas legendas disponíveis para este vídeo.")

        # Prefere json3 por ter timestamps com precisão em milissegundos
        fmt = next((f for f in target_sub if f.get('ext') == 'json3'), target_sub[0])
        sub_url = fmt.get('url')
        if not sub_url:
            raise NoTranscriptFound("URL de legendas não encontrada.")

        res = requests.get(sub_url, timeout=15)
        if res.status_code != 200:
            raise Exception(f"Falha ao baixar arquivo de legendas (HTTP {res.status_code})")

        data = res.json()
        events = data.get('events', [])
        
        normalized_data = []
        formatted_lines = []

        for e in events:
            tStart = e.get('tStartMs', 0) / 1000.0
            dDuration = e.get('dDurationMs', 0) / 1000.0
            segs = e.get('segs', [])
            text = ''.join([s.get('utf8', '') for s in segs]).replace('\n', ' ').strip()
            
            # Filtra eventos vazios ou marcadores
            if text and text != '\n' and text != '[Music]' and text != '[Música]':
                normalized_data.append({
                    "text": text,
                    "start": float(tStart),
                    "duration": float(dDuration)
                })
                start_str = format_timestamp(float(tStart))
                formatted_lines.append(f"[{start_str}] {text}")

        if not normalized_data:
            raise NoTranscriptFound("Transcrição vazia ou não processável.")

        formatted_text = "\n".join(formatted_lines)
        return normalized_data, formatted_text

def get_transcript(video_id: str, preferred_languages: Optional[List[str]] = None) -> Tuple[List[Dict[str, Any]], str]:
    """
    Obtém a transcrição do vídeo com timestamps com fallback de alta disponibilidade.
    Primeiro tenta YouTubeTranscriptApi; se falhar ou der timeout, usa yt-dlp json3.
    """
    if preferred_languages is None:
        preferred_languages = ['pt', 'pt-BR', 'pt-PT', 'en', 'es']

    # 1. Tenta YouTubeTranscriptApi
    try:
        yta = YouTubeTranscriptApi()
        transcript_list = yta.list(video_id)
        
        transcript = None
        try:
            transcript = transcript_list.find_transcript(preferred_languages)
        except Exception:
            try:
                transcript = transcript_list.find_generated_transcript(preferred_languages)
            except Exception:
                for t in transcript_list:
                    transcript = t
                    break

        if transcript:
            raw_data = transcript.fetch()
            normalized_data = []
            formatted_lines = []
            
            for item in raw_data:
                text = getattr(item, 'text', None) or (item.get('text') if isinstance(item, dict) else str(item))
                start = getattr(item, 'start', None) if hasattr(item, 'start') else (item.get('start', 0.0) if isinstance(item, dict) else 0.0)
                duration = getattr(item, 'duration', None) if hasattr(item, 'duration') else (item.get('duration', 0.0) if isinstance(item, dict) else 0.0)
                
                clean_text = str(text).replace('\n', ' ').strip()
                if clean_text:
                    normalized_data.append({
                        "text": clean_text,
                        "start": float(start),
                        "duration": float(duration)
                    })
                    start_str = format_timestamp(float(start))
                    formatted_lines.append(f"[{start_str}] {clean_text}")
                    
            if normalized_data:
                formatted_text = "\n".join(formatted_lines)
                return normalized_data, formatted_text
    except Exception:
        # Se falhar (ex: Timeout ou bloqueio), segue imediatamente para o fallback yt-dlp
        pass

    # 2. Fallback resiliente com yt-dlp
    try:
        return get_transcript_via_ytdlp(video_id, preferred_languages)
    except TranscriptsDisabled:
        raise Exception("As legendas e transcrições estão desativadas neste vídeo.")
    except NoTranscriptFound:
        raise Exception("Não foram encontradas legendas/transcrição disponíveis para este vídeo.")
    except Exception as e:
        raise Exception(f"Erro ao obter transcrição: {str(e)}")

