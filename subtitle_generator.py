import os
from typing import List, Dict, Any, Optional

def format_ass_time(seconds: float) -> str:
    """Converte segundos para o formato de tempo do ASS: H:MM:SS.cs"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centisecs = int(round((seconds - int(seconds)) * 100))
    if centisecs >= 100:
        centisecs = 99
    return f"{hrs}:{mins:02d}:{secs:02d}.{centisecs:02d}"

def generate_ass_subtitles(
    transcript_items: List[Dict[str, Any]], 
    start_time: float, 
    end_time: float, 
    ass_path: str,
    font_name: str = "Arial Black",
    font_size: int = 44,
    style: str = "yellow_black", # 'yellow_black', 'white_yellow', 'neon_green'
    animation: str = "pop" # 'pop', 'fade', 'none'
) -> str:
    """
    Gera arquivo de legendas .ass estilizado para YouTube Shorts e TikTok.
    - Letras em Amarelo (#FFFF00) com borda preta grossa e sombra.
    - Transição Pop-in dinâmica a cada 2 a 4 palavras.
    - Posicionamento otimizado para não cobrir a interface do YouTube Shorts.
    """
    os.makedirs(os.path.dirname(os.path.abspath(ass_path)), exist_ok=True)
    
    # Cores no formato ASS (AABBGGRR):
    # Amarelo: &H0000FFFF (BGR: 00 FF FF)
    # Branco: &H00FFFFFF
    # Verde Neon: &H0000FF00
    if style == "yellow_black":
        primary_color = "&H0000FFFF" # Amarelo vibrante
        outline_color = "&H00000000" # Preto
    elif style == "neon_green":
        primary_color = "&H0024F4EE" # Ciano / Verde Neon
        outline_color = "&H00000000"
    else: # white_yellow
        primary_color = "&H00FFFFFF" # Branco
        outline_color = "&H00000000"

    header = f"""[Script Info]
Title: Shorts Dynamic Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ShortsStyle,{font_name},{font_size},{primary_color},&H00FFFFFF,{outline_color},&H80000000,-1,0,0,0,100,100,2,0,1,8,4,2,60,60,480,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    dialogues = []
    
    for item in transcript_items:
        item_start = float(item.get('start', 0.0))
        item_duration = float(item.get('duration', 0.0))
        item_end = item_start + item_duration
        
        # Ignora blocos fora do intervalo do corte
        if item_end <= start_time or item_start >= end_time:
            continue
            
        rel_start = max(0.0, item_start - start_time)
        rel_end = max(rel_start + 0.2, min(end_time - start_time, item_end - start_time))
        
        raw_text = str(item.get('text', '')).strip().upper()
        if not raw_text:
            continue
            
        # Divide frases em blocos dinâmicos de 2 a 4 palavras (estilo viral de leitura rápida)
        words = raw_text.split()
        if len(words) <= 4:
            chunks = [raw_text]
            chunk_duration = rel_end - rel_start
            time_per_chunk = chunk_duration
        else:
            chunk_size = 3
            chunks = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
            time_per_chunk = (rel_end - rel_start) / len(chunks)
            
        cur_start = rel_start
        for chunk in chunks:
            cur_end = min(end_time - start_time, cur_start + time_per_chunk)
            if cur_end <= cur_start:
                cur_end = cur_start + 0.3
                
            start_str = format_ass_time(cur_start)
            end_str = format_ass_time(cur_end)
            
            # Animações de transição
            if animation == "pop":
                # Efeito Pop / Bounce: Zoom rápido 115% -> 100%
                anim_tag = r"{\t(0,80,\fscx118\fscy118)\t(80,160,\fscx100\fscy100)}"
            elif animation == "fade":
                anim_tag = r"{\fad(80,80)}"
            else:
                anim_tag = ""
                
            dialogues.append(f"Dialogue: 0,{start_str},{end_str},ShortsStyle,,0,0,0,,{anim_tag}{chunk}")
            cur_start = cur_end
            
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(dialogues) + "\n")
        
    return ass_path
