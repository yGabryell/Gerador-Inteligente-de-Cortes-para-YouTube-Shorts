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

def get_cut_transcript_items(transcript_items: List[Dict[str, Any]], start_time: float, end_time: float) -> List[Dict[str, Any]]:
    """Extrai e limpa os itens de transcrição dentro do intervalo do corte."""
    items = []
    for it in transcript_items:
        s = float(it.get('start', 0.0))
        d = float(it.get('duration', 0.0))
        e = s + d
        if e <= start_time or s >= end_time:
            continue
        text = str(it.get('text', '')).strip().replace('\n', ' ')
        if text:
            items.append({
                'start': max(start_time, s),
                'end': min(end_time, e),
                'text': text
            })
    items.sort(key=lambda x: x['start'])
    return items

def generate_ass_subtitles(
    transcript_items: List[Dict[str, Any]], 
    start_time: float, 
    end_time: float, 
    ass_path: str,
    custom_text: Optional[str] = None,
    font_name: str = "Arial Black",
    font_size: int = 78,
    style: str = "yellow_black", # 'yellow_black', 'white_yellow', 'neon_green'
    animation: str = "pop", # 'pop', 'fade', 'none'
    chunk_size: int = 3,
    is_widescreen: bool = False
) -> str:
    """
    Gera arquivo de legendas .ass estilizado para YouTube Shorts e TikTok.
    - Exibe rigorosamente UMA frase/bloco por vez na tela (sem sobreposição/empilhamento).
    - Permite texto customizado/corrigido pelo usuário.
    - Letras em Amarelo (#FFFF00) com borda preta grossa e sombra.
    - Transição Pop-in dinâmica a cada 2 a 4 palavras.
    - Posicionamento otimizado para não cobrir a interface do YouTube Shorts ou Widescreen.
    """
    os.makedirs(os.path.dirname(os.path.abspath(ass_path)), exist_ok=True)
    
    # Cores no formato ASS (AABBGGRR):
    if style == "yellow_black":
        primary_color = "&H0000FFFF" # Amarelo vibrante
        outline_color = "&H00000000" # Preto
    elif style == "neon_green":
        primary_color = "&H0024F4EE" # Ciano / Verde Neon
        outline_color = "&H00000000"
    else: # white_yellow
        primary_color = "&H00FFFFFF" # Branco
        outline_color = "&H00000000"

    # Resolução adaptativa
    if is_widescreen:
        play_x, play_y = 1920, 1080
        margin_v = 110
        calib_font = max(36, int(font_size * 0.72))
    else:
        play_x, play_y = 1080, 1920
        margin_v = 480
        calib_font = font_size

    header = f"""[Script Info]
Title: GravitiCuts Dynamic Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None
PlayResX: {play_x}
PlayResY: {play_y}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ShortsStyle,{font_name},{calib_font},{primary_color},&H00FFFFFF,{outline_color},&H80000000,-1,0,0,0,100,100,2,0,1,8,4,2,60,60,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    # 1. Filtra itens do intervalo ou processa texto customizado editado pelo usuário
    valid_items = get_cut_transcript_items(transcript_items, start_time, end_time)
    
    if custom_text and custom_text.strip():
        lines = [line.strip() for line in custom_text.splitlines() if line.strip()]
        if lines:
            if len(lines) == len(valid_items):
                for idx, line in enumerate(lines):
                    valid_items[idx]['text'] = line
            else:
                total_duration = max(1.0, end_time - start_time)
                line_duration = total_duration / len(lines)
                valid_items = []
                for idx, line in enumerate(lines):
                    l_start = start_time + idx * line_duration
                    l_end = min(end_time, l_start + line_duration)
                    valid_items.append({
                        'start': l_start,
                        'end': l_end,
                        'text': line
                    })

    if not valid_items:
        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(header)
        return ass_path

    # 2. Divide em blocos dinâmicos e ajusta timings estritamente sequenciais
    raw_subtitles = []
    for i, item in enumerate(valid_items):
        item_start = item['start']
        # Limita o fim da frase atual para não invadir o início da próxima
        if i + 1 < len(valid_items):
            next_start = valid_items[i+1]['start']
            item_end = min(item['end'], max(item_start + 0.3, next_start))
        else:
            item_end = item['end']

        words = item['text'].split()
        if not words:
            continue
            
        if len(words) <= 4:
            chunks = [item['text']]
        else:
            chunks = [' '.join(words[j:j+chunk_size]) for j in range(0, len(words), chunk_size)]
            
        total_duration = max(0.4, item_end - item_start)
        chunk_duration = total_duration / len(chunks)
        
        c_start = item_start
        for c_text in chunks:
            c_end = min(end_time, c_start + chunk_duration)
            raw_subtitles.append({
                'rel_start': max(0.0, c_start - start_time),
                'rel_end': max(0.0, min(end_time - start_time, c_end - start_time)),
                'text': c_text.upper()
            })
            c_start = c_end

    # 3. Garante 100% que nenhuma legenda sobreponha a seguinte (evita empilhamento)
    for k in range(len(raw_subtitles) - 1):
        if raw_subtitles[k]['rel_end'] > raw_subtitles[k+1]['rel_start']:
            raw_subtitles[k]['rel_end'] = raw_subtitles[k+1]['rel_start']

    dialogues = []
    for sub in raw_subtitles:
        if sub['rel_end'] <= sub['rel_start']:
            continue
            
        start_str = format_ass_time(sub['rel_start'])
        end_str = format_ass_time(sub['rel_end'])
        
        # Animações de transição
        if animation == "pop":
            anim_tag = r"{\t(0,80,\fscx118\fscy118)\t(80,160,\fscx100\fscy100)}"
        elif animation == "fade":
            anim_tag = r"{\fad(80,80)}"
        else:
            anim_tag = ""
            
        dialogues.append(f"Dialogue: 0,{start_str},{end_str},ShortsStyle,,0,0,0,,{anim_tag}{sub['text']}")
        
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(dialogues) + "\n")
        
    return ass_path
