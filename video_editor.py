import os
import subprocess
from typing import Optional
import imageio_ffmpeg

def get_ffmpeg_path() -> str:
    """Obtém o executável do FFmpeg embutido via imageio-ffmpeg"""
    return imageio_ffmpeg.get_ffmpeg_exe()

def create_short_clip(
    input_path: str,
    start_time: float,
    end_time: float,
    output_path: str,
    mode: str = "blur_bg", # 'blur_bg', 'center_crop', 'original'
    subtitle_ass_path: Optional[str] = None
) -> str:
    """
    Corta o vídeo no intervalo especificado, aplica formatação para Shorts (9:16)
    e opcionalmente queima as legendas animadas (.ass) diretamente no vídeo.
    """
    ffmpeg_exe = get_ffmpeg_path()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    duration = max(1.0, end_time - start_time)

    # Prepara o filtro de legenda se fornecido
    sub_filter = ""
    if subtitle_ass_path and os.path.exists(subtitle_ass_path):
        escaped_sub = os.path.abspath(subtitle_ass_path).replace("\\", "/").replace(":", "\\:")
        sub_filter = f",subtitles=filename='{escaped_sub}'"

    # Filtros de vídeo conforme o modo escolhido
    if mode == "blur_bg":
        # Fundo desfocado 1080x1920 + vídeo centralizado + legenda
        video_filter = (
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];"
            f"[0:v]scale=1080:-2[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2{sub_filter}[v]"
        )
    elif mode == "center_crop":
        # Corte central 1080x1920 + legenda
        video_filter = f"[0:v]crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920{sub_filter}[v]"
    else:
        # Original com legenda opcional
        if sub_filter:
            video_filter = f"[0:v]null{sub_filter}[v]"
        else:
            video_filter = None

    cmd = [
        ffmpeg_exe,
        "-y",                   # Sobrescrever se existir
        "-ss", str(start_time), # Início preciso
        "-i", input_path,
        "-t", str(duration),    # Duração do trecho
    ]

    if video_filter:
        cmd.extend([
            "-filter_complex", video_filter,
            "-map", "[v]",
            "-map", "0:a?",
        ])

    cmd.extend([
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_path
    ])

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Erro ao processar vídeo com FFmpeg: {result.stderr}")
        
    return output_path
