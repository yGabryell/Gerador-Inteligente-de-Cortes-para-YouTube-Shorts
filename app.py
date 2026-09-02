import os
import streamlit as st
from dotenv import load_dotenv

from transcriber import extract_video_id, get_transcript, format_timestamp
from ai_analyzer import find_best_shorts
from video_downloader import get_video_info, download_video, sanitize_filename
from video_editor import create_short_clip
from subtitle_generator import generate_ass_subtitles, get_cut_transcript_items

# Carrega variáveis de ambiente
load_dotenv()

# Configuração da página Streamlit
st.set_page_config(
    page_title="GravitiCuts AI | Studio de Cortes Inteligentes",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Idêntica às Imagens do Dashboard SaaS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Fundo Dark Obsidian / Deep Purple */
    .stApp {
        background-color: #090A10;
        color: #F1F5F9;
    }
    
    /* Header do Streamlit */
    header[data-testid="stHeader"] {
        background: rgba(9, 10, 16, 0.8) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Espaçamento do topo para deixar o título 100% visível e destacado */
    .block-container {
        padding-top: 5.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1400px;
    }
    
    /* Barra Lateral Escura e Minimalista */
    [data-testid="stSidebar"] {
        background-color: #0E101A !important;
        border-right: 1px solid #1C1F33 !important;
        padding-top: 1rem;
    }
    
    /* Topbar Navigation */
    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 20px;
        border-bottom: 1px solid #1A1D2E;
        margin-bottom: 25px;
    }
    .brand-logo {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.3rem;
        font-weight: 800;
        color: #FFFFFF;
    }
    .brand-icon {
        background: linear-gradient(135deg, #8B5CF6, #EC4899);
        width: 34px;
        height: 34px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
    }
    .user-pill {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .credit-badge {
        background: #171A2B;
        border: 1px solid #282C48;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 700;
        color: #A78BFA;
    }
    .free-badge {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #34D399;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
    }
    
    /* Stepper Bar */
    .stepper-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 18px;
        margin-bottom: 30px;
    }
    .step-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 18px;
        border-radius: 25px;
        font-weight: 700;
        font-size: 0.9rem;
    }
    .step-active {
        background: #201D3D;
        border: 1px solid #7C3AED;
        color: #FFFFFF;
    }
    .step-inactive {
        background: #111320;
        border: 1px solid #1C2035;
        color: #64748B;
    }
    
    /* Cards do Dashboard */
    .saas-card {
        background: #111322;
        border: 1px solid #1E2238;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 20px;
    }
    .saas-card-header {
        font-size: 1.05rem;
        font-weight: 800;
        color: #F8FAFC;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Input Box Estilo SaaS */
    .stTextInput > div > div > input {
        background-color: #0A0C16 !important;
        border: 1px solid #232742 !important;
        border-radius: 12px !important;
        color: #FFFFFF !important;
        padding: 12px 16px !important;
        font-size: 0.95rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #8B5CF6 !important;
        box-shadow: 0 0 15px rgba(139, 92, 246, 0.3) !important;
    }
    
    /* HotPeak Cards */
    .hotpeak-item {
        background: #111322;
        border: 1px solid #1F243D;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 20px;
        transition: all 0.2s ease;
    }
    .hotpeak-item:hover {
        border-color: #8B5CF6;
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.2);
    }
    .score-chip {
        background: linear-gradient(135deg, #EC4899, #8B5CF6);
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.78rem;
    }
    .time-chip {
        background: #1A1D33;
        color: #94A3B8;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.78rem;
    }
    .hook-badge-box {
        background: rgba(236, 72, 153, 0.08);
        border-left: 3px solid #EC4899;
        padding: 8px 12px;
        border-radius: 6px;
        margin: 10px 0;
        font-size: 0.85rem;
        color: #FCE7F3;
        font-style: italic;
    }
    
    /* Botões */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 10px 20px !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%) !important;
        border: 1px solid #8B5CF6 !important;
        color: white !important;
        box-shadow: 0 4px 16px rgba(124, 58, 237, 0.35) !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 22px rgba(124, 58, 237, 0.55) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Sidebar Navigation Links */
    .nav-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 14px;
        border-radius: 10px;
        color: #94A3B8;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 4px;
        text-decoration: none;
    }
    .nav-item-active {
        background: #1B1E33;
        color: #FFFFFF;
        border-left: 3px solid #8B5CF6;
    }
    
    /* Free Plan Card */
    .plan-card {
        background: #131525;
        border: 1px solid #222640;
        border-radius: 14px;
        padding: 14px;
        margin-top: 25px;
    }
    
    /* Subtitle Live Preview Box (Proporção Exata 9:16 de Smartphone) */
    .sub-phone-container {
        display: flex;
        justify-content: center;
        margin: 16px 0;
    }
    .sub-phone-mockup {
        width: 180px;
        height: 320px; /* Exato 9:16 (180 * 16 / 9 = 320px) */
        background: #090B14;
        border: 3px solid #2F3554;
        border-radius: 26px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.8), 0 0 20px rgba(139, 92, 246, 0.15);
    }
    .phone-screen {
        width: 100%;
        height: 100%;
        position: relative;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 8px 6px;
        background: linear-gradient(180deg, #1E1B4B 0%, #0F172A 50%, #070914 100%);
    }
    .phone-notch {
        width: 42px;
        height: 4px;
        background: #334155;
        border-radius: 4px;
        margin: 0 auto;
        z-index: 5;
    }
    .phone-badge-tag {
        font-size: 0.62rem;
        font-weight: 800;
        text-transform: uppercase;
        color: #94A3B8;
        letter-spacing: 0.5px;
        text-align: center;
        margin-top: 4px;
        z-index: 5;
    }
    .phone-side-icons {
        position: absolute;
        right: 6px;
        bottom: 50px;
        display: flex;
        flex-direction: column;
        gap: 8px;
        z-index: 4;
        font-size: 0.62rem;
        color: rgba(255, 255, 255, 0.65);
        text-align: center;
    }
    .sub-preview-content {
        position: absolute;
        bottom: 68px; /* ~22-25% do fundo, exatamente MarginV do ASS */
        left: 8px;
        right: 28px;
        text-align: center;
        z-index: 5;
    }
    .sub-preview-text {
        font-family: 'Impact', 'Arial Black', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        line-height: 1.15;
        font-weight: 900;
        display: inline-block;
    }
    
    @keyframes popBounceEffect {
        0%, 100% { transform: scale(1.14); }
        50% { transform: scale(0.96); }
    }
    @keyframes fadeSoftEffect {
        0%, 100% { opacity: 0.3; transform: translateY(2px); }
        50% { opacity: 1; transform: translateY(0); }
    }
    .anim-pop {
        animation: popBounceEffect 0.75s infinite ease-in-out;
    }
    .anim-fade {
        animation: fadeSoftEffect 1.1s infinite ease-in-out;
    }
    
    /* Prévia Widescreen (16:9) */
    .sub-wide-container {
        display: flex;
        justify-content: center;
        margin: 16px 0;
    }
    .sub-wide-mockup {
        width: 100%;
        max-width: 320px;
        height: 180px; /* Exato 16:9 (320 * 9 / 16 = 180px) */
        background: #090B14;
        border: 3px solid #2F3554;
        border-radius: 14px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.8), 0 0 20px rgba(139, 92, 246, 0.15);
    }
    .wide-screen {
        width: 100%;
        height: 100%;
        position: relative;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 8px 12px;
        background: linear-gradient(180deg, #1E1B4B 0%, #0F172A 50%, #070914 100%);
    }
    .wide-badge-tag {
        font-size: 0.65rem;
        font-weight: 800;
        text-transform: uppercase;
        color: #94A3B8;
        letter-spacing: 0.5px;
        text-align: left;
        z-index: 5;
    }
    .wide-preview-content {
        position: absolute;
        bottom: 22px;
        left: 10px;
        right: 10px;
        text-align: center;
        z-index: 5;
    }

    /* Forçar tema escuro de alto contraste em todos os componentes nativos */
    [data-testid="stSelectbox"] div[data-baseweb="select"] {
        background-color: #0A0C16 !important;
        border: 1px solid #232742 !important;
        border-radius: 12px !important;
        color: #FFFFFF !important;
    }
    [data-testid="stSelectbox"] div[data-baseweb="select"] * {
        color: #FFFFFF !important;
    }
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[data-baseweb="menu"] {
        background-color: #131526 !important;
        border: 1px solid #272C49 !important;
        border-radius: 10px !important;
    }
    li[data-baseweb="menu-item"] {
        color: #FFFFFF !important;
        background-color: #131526 !important;
    }
    li[data-baseweb="menu-item"]:hover {
        background-color: #201D3D !important;
        color: #A78BFA !important;
    }
    label, [data-testid="stWidgetLabel"] p {
        color: #CBD5E1 !important;
        font-weight: 600 !important;
    }
    textarea {
        background-color: #0A0C16 !important;
        color: #FFFFFF !important;
        border: 1px solid #232742 !important;
        border-radius: 10px !important;
    }
    div[data-testid="stExpander"] {
        background-color: #0F111E !important;
        border: 1px solid #20243B !important;
        border-radius: 12px !important;
    }
    div[data-testid="stExpander"] details summary {
        color: #E2E8F0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Barra Lateral de Navegação
with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:25px;">
        <div class="brand-icon">⚡</div>
        <div style="font-size:1.2rem; font-weight:900; color:#FFFFFF;">GravitiCuts AI</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="nav-item nav-item-active">📊 Dashboard</div>
    <div class="nav-item">📁 Projetos</div>
    <div class="nav-item">💲 Financeiro</div>
    <div class="nav-item">🎧 Suporte</div>
    <div class="nav-item">💬 Chat IA</div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("⚙️ CONFIGURAÇÕES DE API")
    env_api_key = os.getenv("GEMINI_API_KEY", "")
    api_key_input = st.text_input(
        "Chave Gemini API",
        value=env_api_key,
        type="password",
        help="Sua chave de API do Google Gemini Studio"
    )
    
    st.markdown("""
    <div class="plan-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <span style="font-weight:800; font-size:0.85rem; color:#FFFFFF;">🎁 Plano Ilimitado</span>
            <span style="color:#10B981; font-weight:700; font-size:0.75rem;">● Ativo</span>
        </div>
        <div style="color:#94A3B8; font-size:0.78rem; margin-bottom:10px;">Motor: Gemini 3.6 Flash IA</div>
        <div style="background:#10B981; color:#042F2E; padding:4px 8px; border-radius:6px; font-weight:800; font-size:0.72rem; text-align:center;">
            ⚡ GRAVITICUTS PRONTO
        </div>
    </div>
    """, unsafe_allow_html=True)

# Top Bar (Header)
st.markdown("""
<div class="top-nav">
    <div style="font-size:1.4rem; font-weight:900; color:#FFFFFF;">GravitiCuts AI | Criar Novo Projeto</div>
    <div class="user-pill">
        <span class="credit-badge">💎 Créditos Ilimitados</span>
        <span class="free-badge">Grátis</span>
        <div style="display:flex; align-items:center; gap:8px; background:#141729; padding:4px 12px; border-radius:20px; border:1px solid #232742;">
            <span style="font-size:0.85rem;">🇧🇷 PT-BR</span>
            <span style="font-weight:700; font-size:0.85rem; color:#E2E8F0;">👤 Gabriel Alves</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Inicializa estados de sessão
if "current_step" not in st.session_state:
    st.session_state.current_step = 1
if "cuts" not in st.session_state:
    st.session_state.cuts = []
if "video_info" not in st.session_state:
    st.session_state.video_info = None
if "raw_transcript" not in st.session_state:
    st.session_state.raw_transcript = []
if "downloaded_video_path" not in st.session_state:
    st.session_state.downloaded_video_path = None
if "cfg_url" not in st.session_state:
    st.session_state.cfg_url = ""
if "cfg_video_style" not in st.session_state:
    st.session_state.cfg_video_style = "blur_bg"
if "cfg_enable_subtitles" not in st.session_state:
    st.session_state.cfg_enable_subtitles = True
if "cfg_sub_style" not in st.session_state:
    st.session_state.cfg_sub_style = "yellow_black"
if "cfg_sub_anim" not in st.session_state:
    st.session_state.cfg_sub_anim = "pop"
if "cfg_sub_fontsize" not in st.session_state:
    st.session_state.cfg_sub_fontsize = 78

# Stepper Dinâmico (1. Configurar -> 2. Processar)
if st.session_state.current_step == 1:
    st.markdown("""
    <div class="stepper-container">
        <div class="step-item step-active">
            <span>⚙️</span> 1. Configurar Projeto
        </div>
        <div style="color:#334155;">──────</div>
        <div class="step-item step-inactive">
            <span>✨</span> 2. Processar e Exportar
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="stepper-container">
        <div class="step-item step-inactive" style="color:#10B981; border-color:rgba(16,185,129,0.4); background:rgba(16,185,129,0.1);">
            <span>✅</span> 1. Configuração Concluída
        </div>
        <div style="color:#8B5CF6;">──────</div>
        <div class="step-item step-active">
            <span>✨</span> 2. Processar e Exportar
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# ETAPA 1: CONFIGURAÇÃO DO PROJETO
# ==============================================================================
if st.session_state.current_step == 1:
    # Card 1: Input da URL do Vídeo
    st.markdown("""
    <div class="saas-card">
        <div class="saas-card-header">
            <span>🔗</span> Cole o link do YouTube (Vídeo, Live ou Podcast)
        </div>
    </div>
    """, unsafe_allow_html=True)

    url_input = st.text_input(
        "URL do YouTube",
        value=st.session_state.cfg_url,
        placeholder="https://www.youtube.com/watch?v=... ou https://youtu.be/...",
        label_visibility="collapsed"
    )
    st.caption("📁 A IA do GravitiCuts fará um raio-x da transcrição para encontrar os momentos com maior força de atração e retenção.")

    # Card 2: Opções de Configuração na Esquerda e Celular Dedicado na Direita
    st.markdown("<br>", unsafe_allow_html=True)
    col_cfg1, col_cfg2 = st.columns([1.15, 0.85], gap="large")

    with col_cfg1:
        # 1. Proporção & Formato
        with st.container():
            st.markdown("""
            <div class="saas-card">
                <div class="saas-card-header">📱 Proporção & Formato</div>
            </div>
            """, unsafe_allow_html=True)
            video_style = st.selectbox(
                "Proporção do Vídeo",
                options=[
                    ("blur_bg", "📱 Vertical (9:16) - TikTok, Reels, Shorts (Fundo Desfocado)"),
                    ("center_crop", "📱 Vertical (9:16) - Corte Centralizado"),
                    ("original", "🖥️ Horizontal (16:9) - Formato Original")
                ],
                format_func=lambda x: x[1],
                label_visibility="collapsed"
            )[0]

        # 2. Legendas nos Cortes (Com Legenda vs Sem Legenda)
        with st.container():
            st.markdown("""
            <div class="saas-card">
                <div class="saas-card-header">💬 Legendas nos Cortes</div>
            </div>
            """, unsafe_allow_html=True)
            
            sub_option = st.radio(
                "Opção de Legenda:",
                options=[
                    ("with_sub", "✨ Com Legendas Dinâmicas (Estilizadas)"),
                    ("no_sub", "🚫 Sem Legenda (Vídeo Limpo)")
                ],
                format_func=lambda x: x[1],
                label_visibility="collapsed",
                horizontal=True
            )[0]
            enable_subtitles = (sub_option == "with_sub")
            
            if enable_subtitles:
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    sub_style = st.selectbox(
                        "Estilo da Legenda",
                        options=[
                            ("yellow_black", "🟡 Amarelo Gamer (Borda Preta)"),
                            ("white_yellow", "⚪ Branco Hormozi (Borda Preta)"),
                            ("neon_green", "🟢 Ciano / Neon")
                        ],
                        format_func=lambda x: x[1]
                    )[0]
                with col_s2:
                    sub_anim = st.selectbox(
                        "Animação",
                        options=[
                            ("pop", "💥 Pop / Bounce (Dinâmico)"),
                            ("fade", "✨ Fade Suave"),
                            ("none", "Estática")
                        ],
                        format_func=lambda x: x[1]
                    )[0]
                sub_fontsize = st.slider("Tamanho da Legenda no Vídeo (px)", min_value=50, max_value=120, value=78, step=2, help="Padrão recomendado para Shorts: 75 a 85px")
            else:
                sub_style = "yellow_black"
                sub_anim = "pop"
                sub_fontsize = 78
                st.markdown("""
                <div style="background:#0E101D; border:1px solid #1E2238; border-radius:10px; padding:12px 14px; color:#94A3B8; font-size:0.86rem; margin-top:8px;">
                    🎬 <strong>Modo Vídeo Limpo:</strong> Os cortes serão exportados na proporção escolhida sem nenhuma legenda queimada na tela.
                </div>
                """, unsafe_allow_html=True)
            
        # 3. Duração dos Cortes
        with st.container():
            st.markdown("""
            <div class="saas-card">
                <div class="saas-card-header">⏱️ Duração dos Cortes (IA Automática)</div>
            </div>
            """, unsafe_allow_html=True)
            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1:
                num_cuts = st.number_input("Cortes", min_value=1, max_value=12, value=6)
            with col_d2:
                min_sec = st.number_input("Mín (s)", min_value=15, max_value=60, value=30)
            with col_d3:
                max_sec = st.number_input("Máx (s)", min_value=30, max_value=180, value=60)

        # 4. Instrução Personalizada
        with st.container():
            st.markdown("""
            <div class="saas-card">
                <div class="saas-card-header">🎯 Instrução Personalizada para a IA (Opcional)</div>
            </div>
            """, unsafe_allow_html=True)
            custom_prompt = st.text_input(
                "Prompt Personalizado",
                placeholder="Ex: Quero cortes com jogadas incríveis, explicações claras, momentos engraçados...",
                label_visibility="collapsed"
            )
            st.caption("Sugestões: Informativos • Engraçados • Polêmicos • Insights • Melhores Jogadas")

    with col_cfg2:
        # Coluna Dinâmica de Prévia (Smartphone 9:16 ou Widescreen 16:9)
        is_widescreen = (video_style == "original" or "16:9" in str(video_style))
        preview_title = "Prévia em Tempo Real (16:9)" if is_widescreen else "Prévia em Tempo Real (9:16)"
        preview_icon = "🖥️" if is_widescreen else "📱"
        
        with st.container():
            st.markdown(f"""
            <div class="saas-card" style="text-align:center; padding:18px 12px;">
                <div class="saas-card-header" style="justify-content:center;">
                    <span>{preview_icon}</span> {preview_title}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if enable_subtitles:
                if sub_style == "yellow_black":
                    color_css = "color: #FFE600; text-shadow: -2.5px -2.5px 0 #000, 2.5px -2.5px 0 #000, -2.5px 2.5px 0 #000, 2.5px 2.5px 0 #000, 0 4px 10px rgba(0,0,0,0.9);"
                elif sub_style == "white_yellow":
                    color_css = "color: #FFFFFF; text-shadow: -2.5px -2.5px 0 #000, 2.5px -2.5px 0 #000, -2.5px 2.5px 0 #000, 2.5px 2.5px 0 #000, 0 4px 10px rgba(0,0,0,0.9);"
                else: # neon_green
                    color_css = "color: #00F0FF; text-shadow: -2.5px -2.5px 0 #000, 2.5px -2.5px 0 #000, -2.5px 2.5px 0 #000, 2.5px 2.5px 0 #000, 0 0 16px rgba(0,240,255,0.85);"

                anim_css_class = "anim-pop" if sub_anim == "pop" else ("anim-fade" if sub_anim == "fade" else "")
                preview_font_size = max(11, int(sub_fontsize * 0.165))

                if is_widescreen:
                    mockup_html = (
                        f'<div class="sub-wide-container">'
                        f'<div class="sub-wide-mockup">'
                        f'<div class="wide-screen">'
                        f'<div style="display:flex; justify-content:space-between; align-items:center;">'
                        f'<div class="wide-badge-tag">🖥️ 16:9 Widescreen Preview</div>'
                        f'<div style="font-size:0.6rem; color:#94A3B8;">🔴 1080p</div>'
                        f'</div>'
                        f'<div class="wide-preview-content">'
                        f'<div class="sub-preview-text {anim_css_class}" style="{color_css} font-size: {preview_font_size}px;">'
                        f'OLHA ESSA JOGADA! 🔥'
                        f'</div>'
                        f'</div>'
                        f'<div style="display:flex; justify-content:space-between; align-items:center; font-size:0.6rem; color:#94A3B8; z-index:5;">'
                        f'<span>▶️ 01:24 / 08:30</span>'
                        f'<span>⚙️ 1080p60 🔲</span>'
                        f'</div>'
                        f'</div>'
                        f'</div>'
                        f'</div>'
                    )
                else:
                    mockup_html = (
                        f'<div class="sub-phone-container">'
                        f'<div class="sub-phone-mockup">'
                        f'<div class="phone-screen">'
                        f'<div>'
                        f'<div class="phone-notch"></div>'
                        f'<div class="phone-badge-tag">📱 9:16 Shorts Preview</div>'
                        f'</div>'
                        f'<div class="phone-side-icons">'
                        f'<div>❤️<br><span style="font-size:0.52rem;">42K</span></div>'
                        f'<div>💬<br><span style="font-size:0.52rem;">1.2K</span></div>'
                        f'<div>↗️<br><span style="font-size:0.52rem;">Share</span></div>'
                        f'</div>'
                        f'<div class="sub-preview-content">'
                        f'<div class="sub-preview-text {anim_css_class}" style="{color_css} font-size: {preview_font_size}px;">'
                        f'OLHA ESSA JOGADA! 🔥'
                        f'</div>'
                        f'</div>'
                        f'</div>'
                        f'</div>'
                        f'</div>'
                    )
                st.markdown(mockup_html, unsafe_allow_html=True)
                st.caption(f"<div style='text-align:center; color:#94A3B8; margin-top:8px;'>✨ Acompanhe ao vivo as cores, animação e tamanho exato para os seus cortes {('16:9' if is_widescreen else '9:16')}.</div>", unsafe_allow_html=True)
            else:
                # Prévia do vídeo LIMPO (sem legendas)
                if is_widescreen:
                    mockup_html = (
                        f'<div class="sub-wide-container">'
                        f'<div class="sub-wide-mockup">'
                        f'<div class="wide-screen">'
                        f'<div style="display:flex; justify-content:space-between; align-items:center;">'
                        f'<div class="wide-badge-tag">🖥️ 16:9 Widescreen</div>'
                        f'<div style="font-size:0.6rem; color:#10B981;">● Vídeo Limpo</div>'
                        f'</div>'
                        f'<div class="wide-preview-content">'
                        f'<div style="color:rgba(255,255,255,0.45); font-size:0.8rem; font-weight:700;">'
                        f'🎬 Sem Legendas'
                        f'</div>'
                        f'</div>'
                        f'<div style="display:flex; justify-content:space-between; align-items:center; font-size:0.6rem; color:#94A3B8; z-index:5;">'
                        f'<span>▶️ 01:24 / 08:30</span>'
                        f'<span>⚙️ 1080p60 🔲</span>'
                        f'</div>'
                        f'</div>'
                        f'</div>'
                        f'</div>'
                    )
                else:
                    mockup_html = (
                        f'<div class="sub-phone-container">'
                        f'<div class="sub-phone-mockup">'
                        f'<div class="phone-screen">'
                        f'<div>'
                        f'<div class="phone-notch"></div>'
                        f'<div class="phone-badge-tag">📱 9:16 Shorts</div>'
                        f'</div>'
                        f'<div class="phone-side-icons">'
                        f'<div>❤️<br><span style="font-size:0.52rem;">42K</span></div>'
                        f'<div>💬<br><span style="font-size:0.52rem;">1.2K</span></div>'
                        f'<div>↗️<br><span style="font-size:0.52rem;">Share</span></div>'
                        f'</div>'
                        f'<div class="sub-preview-content">'
                        f'<div style="color:rgba(255,255,255,0.45); font-size:0.8rem; font-weight:700;">'
                        f'🎬 Sem Legendas'
                        f'</div>'
                        f'</div>'
                        f'</div>'
                        f'</div>'
                        f'</div>'
                    )
                st.markdown(mockup_html, unsafe_allow_html=True)
                st.caption(f"<div style='text-align:center; color:#94A3B8; margin-top:8px;'>✨ Prévia do seu corte {('16:9' if is_widescreen else '9:16')} sem legendas (vídeo original limpo).</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Botão Principal de Ação
    col_act1, col_act2, col_act3 = st.columns([1, 2, 1])
    with col_act2:
        analyze_btn = st.button("⚡ Gerar Cortes com GravitiCuts IA", type="primary", use_container_width=True)

    # Ação do Botão Principal (Muda IMEDIATAMENTE para a Página 2)
    if analyze_btn:
        if not url_input.strip():
            st.warning("⚠️ Por favor, insira o link do vídeo do YouTube.")
        else:
            video_id = extract_video_id(url_input)
            if not video_id:
                st.error("❌ Não foi possível identificar o vídeo. Verifique a URL.")
            else:
                # Salva todas as opções no session_state
                st.session_state.cfg_url = url_input
                st.session_state.cfg_video_id = video_id
                st.session_state.cfg_video_style = video_style
                st.session_state.cfg_enable_subtitles = enable_subtitles
                st.session_state.cfg_sub_style = sub_style
                st.session_state.cfg_sub_anim = sub_anim
                st.session_state.cfg_sub_fontsize = sub_fontsize
                st.session_state.cfg_num_cuts = num_cuts
                st.session_state.cfg_min_sec = min_sec
                st.session_state.cfg_max_sec = max_sec
                st.session_state.cfg_custom_prompt = custom_prompt
                
                # Ativa processamento e transita IMEDIATAMENTE para a Etapa 2
                st.session_state.is_processing = True
                st.session_state.cuts = []
                st.session_state.current_step = 2
                st.rerun()

# ==============================================================================
# ETAPA 2: PROCESSAR E EXPORTAR (PÁGINA 2)
# ==============================================================================
elif st.session_state.current_step == 2:
    # SE ESTIVER PROCESSANDO: EXIBE EXCLUSIVAMENTE A TELA DE CARREGAMENTO
    if st.session_state.get("is_processing", False):
        col_c1, col_c2 = st.columns([1, 4])
        with col_c1:
            if st.button("⬅️ Cancelar", use_container_width=True):
                st.session_state.is_processing = False
                st.session_state.current_step = 1
                st.rerun()
                
        status_slot = st.empty()
        progress_bar = st.progress(20)
        
        # Etapa 1
        status_slot.markdown("""
        <div class="saas-card" style="text-align:center; padding:45px 20px; border:1px solid #7C3AED; box-shadow:0 0 35px rgba(124,58,237,0.25);">
            <div style="font-size:3rem; margin-bottom:14px;">📥⚡</div>
            <div style="font-size:1.45rem; font-weight:800; color:#FFFFFF; margin-bottom:8px;">Etapa 1/3: Coletando Metadados do Vídeo</div>
            <div style="color:#A78BFA; font-size:0.95rem;">Buscando título, canal, miniatura e duração original...</div>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            video_info = get_video_info(st.session_state.cfg_url)
            st.session_state.video_info = video_info
        except Exception as e:
            video_info = {"title": "Vídeo do YouTube", "duration": 0, "thumbnail": "", "channel": ""}
            st.session_state.video_info = video_info

        # Etapa 2
        progress_bar.progress(55)
        status_slot.markdown("""
        <div class="saas-card" style="text-align:center; padding:45px 20px; border:1px solid #7C3AED; box-shadow:0 0 35px rgba(124,58,237,0.25);">
            <div style="font-size:3rem; margin-bottom:14px;">📝⚡</div>
            <div style="font-size:1.45rem; font-weight:800; color:#FFFFFF; margin-bottom:8px;">Etapa 2/3: Extraindo Transcrição e Timestamps</div>
            <div style="color:#A78BFA; font-size:0.95rem;">Lendo e sincronizando as legendas para análise precisa...</div>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            raw_transcript, formatted_transcript = get_transcript(st.session_state.cfg_video_id)
            st.session_state.raw_transcript = raw_transcript
            st.session_state.formatted_transcript = formatted_transcript
        except Exception as e:
            st.error(f"❌ {str(e)}")
            st.session_state.is_processing = False
            st.stop()

        # Etapa 3
        progress_bar.progress(85)
        status_slot.markdown("""
        <div class="saas-card" style="text-align:center; padding:45px 20px; border:1px solid #7C3AED; box-shadow:0 0 35px rgba(124,58,237,0.25);">
            <div style="font-size:3rem; margin-bottom:14px;">🧠⚡</div>
            <div style="font-size:1.45rem; font-weight:800; color:#FFFFFF; margin-bottom:8px;">Etapa 3/3: GravitiCuts IA Minerando Picos Virais</div>
            <div style="color:#A78BFA; font-size:0.95rem;">Calculando HotPeaks de retenção, ganchos magnéticos e histórias completas...</div>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            title_context = f"{video_info.get('title', '')}. Foco: {st.session_state.cfg_custom_prompt}" if st.session_state.cfg_custom_prompt else video_info.get("title", "")
            cuts = find_best_shorts(
                formatted_transcript=st.session_state.formatted_transcript,
                video_title=title_context,
                min_duration=st.session_state.cfg_min_sec,
                max_duration=st.session_state.cfg_max_sec,
                num_cuts=st.session_state.cfg_num_cuts,
                api_key=api_key_input
            )
            progress_bar.progress(100)
            st.session_state.cuts = cuts
            st.session_state.is_processing = False
            st.rerun()
        except Exception as e:
            st.error(f"❌ Erro na análise com IA: {str(e)}")
            st.session_state.is_processing = False
            st.stop()

    # SE O PROCESSAMENTO ESTIVER CONCLUÍDO: MOSTRA O FEED DE CORTES DA PÁGINA 2
    else:
        # Barra de Ações Superior
        col_nav1, col_nav2 = st.columns([1, 4])
        with col_nav1:
            if st.button("⬅️ Configurar Outro Vídeo", use_container_width=True):
                st.session_state.current_step = 1
                st.session_state.is_processing = False
                st.rerun()
        with col_nav2:
            st.markdown(f"""
            <div style="background:#131628; border:1px solid #252A47; padding:8px 16px; border-radius:12px; display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:800; color:#A78BFA; font-size:0.95rem;">🔥 {len(st.session_state.cuts)} Cortes Virais Prontos para Edição</span>
                <span style="font-size:0.8rem; color:#94A3B8;">Formato: <strong>{st.session_state.cfg_video_style}</strong> | Legendas: <strong>{'Ativadas' if st.session_state.cfg_enable_subtitles else 'Desativadas'}</strong></span>
            </div>
            """, unsafe_allow_html=True)

        # Card de Resumo do Vídeo Original
        if st.session_state.video_info:
            v_info = st.session_state.video_info
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="saas-card" style="display:flex; gap:20px; align-items:center;">
                <img src="{v_info.get('thumbnail', '')}" style="width:150px; border-radius:10px; object-fit:cover;">
                <div>
                    <div style="font-weight:800; font-size:1.15rem; color:#FFFFFF; margin-bottom:4px;">{v_info.get('title', '')}</div>
                    <div style="color:#94A3B8; font-size:0.88rem;">👤 Canal: <strong style="color:#CBD5E1;">{v_info.get('channel', 'Desconhecido')}</strong> &nbsp;|&nbsp; ⏱️ Duração: <strong style="color:#CBD5E1;">{format_timestamp(v_info.get('duration', 0))}</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Grid de Cortes Sugeridos (Estilo Feed de Cortes)
        if st.session_state.cuts:
            current_video_id = extract_video_id(st.session_state.cfg_url)
            grid_columns = 3 # 3 colunas padrão
            
            for row_idx in range(0, len(st.session_state.cuts), grid_columns):
                cols = st.columns(grid_columns)
                
                for col_idx in range(grid_columns):
                    cut_idx = row_idx + col_idx
                    if cut_idx < len(st.session_state.cuts):
                        cut = st.session_state.cuts[cut_idx]
                        with cols[col_idx]:
                            # Card Individual do Corte
                            st.markdown(f"""
                            <div class="hotpeak-item">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                                    <span class="score-chip">🔥 PICO VIRAL {cut['score']}%</span>
                                    <span class="time-chip">⏱️ {format_timestamp(cut['start_time'])} - {format_timestamp(cut['end_time'])} ({cut['duration']}s)</span>
                                </div>
                                <div style="font-weight:800; font-size:1.02rem; color:#FFFFFF; line-height:1.35; margin-bottom:8px;">
                                    #{cut_idx+1} {cut['title']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Player do Vídeo Original no Segundo Exato
                            if current_video_id:
                                yt_start = int(cut['start_time'])
                                st.video(f"https://www.youtube.com/watch?v={current_video_id}", start_time=yt_start)
                            
                            # Gancho de Retenção
                            if cut.get('hook'):
                                st.markdown(f"""
                                <div class="hook-badge-box">
                                    <strong>🎯 Gancho (Hook):</strong> "{cut['hook']}"
                                </div>
                                """, unsafe_allow_html=True)
                                
                            if cut.get('reason'):
                                st.caption(f"💡 {cut['reason']}")
                                
                            # 📝 Editor de Legendas do Corte
                            cut_items = get_cut_transcript_items(st.session_state.raw_transcript, cut['start_time'], cut['end_time'])
                            default_lines = "\n".join([it['text'] for it in cut_items])
                            
                            edited_key = f"edited_sub_{cut_idx}"
                            if edited_key not in st.session_state or not st.session_state[edited_key]:
                                st.session_state[edited_key] = default_lines
                                
                            with st.expander("📝 Revisar / Editar Texto da Legenda", expanded=False):
                                st.caption("Corrija palavras erradas ou gírias antes de exportar:")
                                user_text = st.text_area(
                                    f"Legenda #{cut_idx+1}",
                                    value=st.session_state[edited_key],
                                    height=90,
                                    key=f"ta_sub_{cut_idx}",
                                    label_visibility="collapsed"
                                )
                                st.session_state[edited_key] = user_text

                            # Botões para Renderizar o Vídeo (Com Legenda ou Sem Legenda)
                            col_b1, col_b2 = st.columns(2)
                            if st.session_state.get("cfg_enable_subtitles", True):
                                with col_b1:
                                    btn_with_sub = st.button("✂️ Com Legenda", key=f"btn_sub_{cut_idx}", type="primary", use_container_width=True)
                                with col_b2:
                                    btn_no_sub = st.button("🎬 Sem Legenda", key=f"btn_nosub_{cut_idx}", use_container_width=True)
                            else:
                                with col_b1:
                                    btn_no_sub = st.button("🎬 Sem Legenda", key=f"btn_nosub_{cut_idx}", type="primary", use_container_width=True)
                                with col_b2:
                                    btn_with_sub = st.button("✂️ Com Legenda", key=f"btn_sub_{cut_idx}", use_container_width=True)
                                
                            if btn_with_sub or btn_no_sub:
                                is_subbed = bool(btn_with_sub)
                                label_status = "com Legendas" if is_subbed else "sem Legendas"
                                with st.spinner(f"Renderizando Corte #{cut_idx+1} {label_status}..."):
                                    try:
                                        # 1. Download
                                        if not st.session_state.downloaded_video_path or not os.path.exists(st.session_state.downloaded_video_path):
                                            st.info("📥 Baixando vídeo original em alta qualidade...")
                                            downloaded_file = download_video(st.session_state.cfg_url, video_id=current_video_id)
                                            st.session_state.downloaded_video_path = downloaded_file
                                        
                                        # 2. Legendas (se solicitado)
                                        sub_path = None
                                        safe_title = sanitize_filename(cut['title'])[:30]
                                        if is_subbed:
                                            is_wide_cut = (st.session_state.cfg_video_style == "original" or "16:9" in str(st.session_state.cfg_video_style))
                                            ass_filename = f"output/sub_{cut_idx+1}_{safe_title}.ass"
                                            sub_path = generate_ass_subtitles(
                                                transcript_items=st.session_state.raw_transcript,
                                                start_time=cut['start_time'],
                                                end_time=cut['end_time'],
                                                ass_path=ass_filename,
                                                custom_text=st.session_state.get(edited_key),
                                                font_size=st.session_state.cfg_sub_fontsize,
                                                style=st.session_state.cfg_sub_style,
                                                animation=st.session_state.cfg_sub_anim,
                                                is_widescreen=is_wide_cut
                                            )

                                        # 3. Corte e Formatação
                                        output_suffix = "sub" if is_subbed else "clean"
                                        output_filename = f"output/short_{cut_idx+1}_{output_suffix}_{safe_title}.mp4"
                                        
                                        short_path = create_short_clip(
                                            input_path=st.session_state.downloaded_video_path,
                                            start_time=cut['start_time'],
                                            end_time=cut['end_time'],
                                            output_path=output_filename,
                                            mode=st.session_state.cfg_video_style,
                                            subtitle_ass_path=sub_path
                                        )
                                        
                                        st.session_state[f"ready_video_{cut_idx}"] = short_path
                                        st.success(f"✅ Vídeo #{cut_idx+1} {label_status} pronto para download!")
                                    except Exception as e:
                                        st.error(f"Erro ao gerar vídeo: {str(e)}")

                            # Exibição do vídeo vertical pronto e download
                            if f"ready_video_{cut_idx}" in st.session_state:
                                video_file_path = st.session_state[f"ready_video_{cut_idx}"]
                                if os.path.exists(video_file_path):
                                    st.markdown("##### 📱 Short 9:16 Finalizado:")
                                    st.video(video_file_path)
                                    with open(video_file_path, "rb") as file_data:
                                        st.download_button(
                                            label=f"⬇️ Baixar Short #{cut_idx+1} (.mp4)",
                                            data=file_data,
                                            file_name=os.path.basename(video_file_path),
                                            mime="video/mp4",
                                            key=f"dl_{cut_idx}",
                                            use_container_width=True
                                        )
                            
                            st.markdown("<br>", unsafe_allow_html=True)
