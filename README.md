# ⚡ ViralShorts AI - Gerador Automático de Cortes para YouTube Shorts

Plataforma Web open-source para transformar vídeos longos, podcasts e lives do YouTube em **Shorts / TikToks / Reels no formato 9:16**, com análise de viralidade por **Inteligência Artificial (Google Gemini)** e **legendas dinâmicas animadas**.

---

## 🌟 Funcionalidades

- 📥 **Download & Extração Automática:** Obtém metadados e legendas com timestamps em segundos via `youtube-transcript-api` e `yt-dlp`.
- 🧠 **Análise com IA (Gemini 3.6 / Flash):** Identifica os momentos com maior potencial de retenção (*HotPeaks*), ganchos iniciais (*hooks*) e histórias completas.
- 📱 **Enquadramento 9:16 Vertical:** Converte vídeos 16:9 em formato vertical com fundo desfocado (*blurred backdrop*) ou corte centralizado.
- 💬 **Legendas Animadas (TikTok Style):** Queima legendas em amarelo vibrante com borda preta espessa e animação *Pop/Bounce* para retenção máxima.
- 🎨 **Interface SaaS Moderna:** Dashboard inspirado no *Real Oficial* e *ViralShorts AI*, com feed de prévia instantânea e download em `.mp4`.

---

## 🚀 Como Instalar e Rodar

### 1. Clonar o repositório
```bash
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd lucid-meitner
```

### 2. Instalar dependências
Certifique-se de ter o **Python 3.10+** instalado:
```bash
pip install -r requirements.txt
```

### 3. Configurar Chave de API
Copie o arquivo `.env.example` para `.env` e insira sua chave gratuita do [Google AI Studio](https://aistudio.google.com/):
```env
GEMINI_API_KEY=sua_chave_gemini_aqui
```

### 4. Iniciar a Aplicação Web
```bash
streamlit run app.py
```
Ou no Windows, dê dois cliques em `iniciar_app.bat`.

---

## 🛠️ Tecnologias Utilizadas

- **Interface:** [Streamlit](https://streamlit.io/)
- **IA / LLM:** [Google GenAI SDK (Gemini)](https://ai.google.dev/)
- **Download:** [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- **Speech-to-Text / Legendas:** [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)
- **Processamento de Vídeo:** [imageio-ffmpeg / FFmpeg](https://github.com/imageio/imageio-ffmpeg)
