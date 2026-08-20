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

def get_transcript(video_id: str, preferred_languages: Optional[List[str]] = None) -> Tuple[List[Dict[str, Any]], str]:
    """
    Obtém a transcrição do vídeo com timestamps.
    Retorna uma tupla: (lista de itens com {'text', 'start', 'duration'}, texto_formatado_para_ia)
    """
    if preferred_languages is None:
        preferred_languages = ['pt', 'pt-BR', 'en', 'es']

    try:
        yta = YouTubeTranscriptApi()
        transcript_list = yta.list(video_id)
        
        # Tenta encontrar transcrição manual ou automática nas línguas preferidas
        transcript = None
        try:
            transcript = transcript_list.find_transcript(preferred_languages)
        except Exception:
            try:
                transcript = transcript_list.find_generated_transcript(preferred_languages)
            except Exception:
                # Pega a primeira transcrição disponível no vídeo
                for t in transcript_list:
                    transcript = t
                    break

        if not transcript:
            raise NoTranscriptFound("Nenhuma transcrição encontrada para este vídeo.")

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
                
        formatted_text = "\n".join(formatted_lines)
        return normalized_data, formatted_text

    except TranscriptsDisabled:
        raise Exception("As legendas e transcrições estão desativadas neste vídeo.")
    except NoTranscriptFound:
        raise Exception("Não foram encontradas legendas/transcrição disponíveis para este vídeo.")
    except Exception as e:
        raise Exception(f"Erro ao obter transcrição: {str(e)}")
