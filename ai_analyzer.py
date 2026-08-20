import os
import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Carrega o .env localizado no diretório do projeto
PROJECT_DIR = Path(__file__).parent
load_dotenv(PROJECT_DIR / ".env")

# Modelos recomendados em ordem de preferência e eficiência de cota
FALLBACK_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.7-flash",
    "gemini-3.5-flash",
    "gemini-flash-latest",
    "gemini-flash-lite-latest"
]

def get_client(api_key: Optional[str] = None) -> genai.Client:
    """Cria e retorna uma instância do cliente Gemini GenAI"""
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("Chave da API Gemini não encontrada. Defina GEMINI_API_KEY no arquivo .env ou informe na interface.")
    return genai.Client(api_key=key)

def clean_json_response(raw_text: str) -> str:
    """Extrai e limpa a resposta JSON retornada pelo modelo"""
    text = raw_text.strip()
    
    # Remove blocos de código markdown como ```json ... ```
    if "```" in text:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            text = match.group(1).strip()
            
    return text

def parse_time_to_seconds(time_val: Any) -> float:
    """Converte 'MM:SS' ou 'HH:MM:SS' ou número para float em segundos"""
    if isinstance(time_val, (int, float)):
        return float(time_val)
    
    if isinstance(time_val, str):
        parts = time_val.strip().split(':')
        try:
            if len(parts) == 3: # HH:MM:SS
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
            elif len(parts) == 2: # MM:SS
                return float(parts[0]) * 60 + float(parts[1])
            else:
                return float(time_val)
        except ValueError:
            return 0.0
    return 0.0

def find_best_shorts(
    formatted_transcript: str, 
    video_title: str = "", 
    min_duration: int = 25, 
    max_duration: int = 65,
    num_cuts: int = 5,
    api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Analisa a transcrição com a API Gemini e retorna os melhores cortes para Shorts.
    """
    client = get_client(api_key)

    prompt = f"""
Você é um editor sênior especialista em YouTube Shorts, TikTok e Reels com mais de 100 milhões de visualizações.
Sua missão é analisar a transcrição de um vídeo e identificar os {num_cuts} MELHORES momentos para transformar em cortes virais (Shorts).

INFORMAÇÕES DO VÍDEO:
Título: {video_title if video_title else "Vídeo do YouTube"}

CRITÉRIOS OBRIGATÓRIOS PARA CADA CORTE:
1. **Duração:** Cada corte DEVE ter entre {min_duration} e {max_duration} segundos de duração.
2. **Gancho Forte (Hook):** Os primeiros 3 segundos devem prender a atenção imediatamente (uma frase impactante, pergunta intrigante, revelação ou momento de humor).
3. **Sentido Completo:** O corte DEVE ter começo, meio e fim claros. NUNCA corte no meio de uma frase ou raciocínio.
4. **Potencial Viral:** Priorize momentos emocionantes, histórias surpreendentes, lições valiosas, opiniões fortes ou quebras de expectativa.

TRANSCRIÇÃO COM TIMESTAMPS:
{formatted_transcript}

FORMATO DE RESPOSTA OBRIGATÓRIO (APENAS JSON):
Retorne ESTRITAMENTE um array JSON contendo os melhores cortes, sem texto antes ou depois:
[
  {{
    "title": "Título muito chamativo e curto para o Short",
    "start_time": 120.0,
    "end_time": 168.5,
    "hook": "A frase exata que inicia o corte com impacto",
    "summary": "Resumo em 1 frase do que acontece",
    "score": 95,
    "reason": "Por que esse trecho tem alto potencial de viralização"
  }}
]

Atenção: `start_time` e `end_time` devem ser números em segundos (ex: 125.0) correspondentes aos timestamps exatos da transcrição.
"""

    last_error = None
    for model_name in FALLBACK_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3
                )
            )
            cleaned_text = clean_json_response(response.text)
            cuts_data = json.loads(cleaned_text)
            
            # Valida e normaliza os cortes
            normalized_cuts = []
            for cut in cuts_data:
                start = parse_time_to_seconds(cut.get("start_time", 0))
                end = parse_time_to_seconds(cut.get("end_time", 0))
                duration = max(0.0, end - start)
                
                normalized_cuts.append({
                    "title": cut.get("title", "Corte sem título"),
                    "start_time": start,
                    "end_time": end,
                    "duration": round(duration, 1),
                    "hook": cut.get("hook", ""),
                    "summary": cut.get("summary", ""),
                    "score": int(cut.get("score", 85)),
                    "reason": cut.get("reason", "")
                })

            # Ordena pelos com maior pontuação (score)
            normalized_cuts.sort(key=lambda x: x["score"], reverse=True)
            return normalized_cuts

        except Exception as e:
            last_error = e
            continue

    raise Exception(f"Falha ao processar com os modelos Gemini disponíveis: {str(last_error)}")
