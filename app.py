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

# Estilização CSS Moderna, Responsiva e com Animações Fluidas (Glassmorphism & Cyber Obsidian 2026)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&display=swap');
    
    html, body, [class*="css"], .stApp, p, h1, h2, h3, h4, h5, h6, label, input, textarea, button {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    *, *::before, *::after {
        box-sizing: border-box;
    }

    /* Preservar ícones do Streamlit (Material Symbols / Icons) como o olho de senha */
    [data-testid="stIconMaterial"], [class*="material-symbols"], [class*="material-icons"], span[translate="no"] {
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
    }
    
    /* Fundo Dark Obsidian com Aura Glow Ambiental */
    .stApp {
        background-color: #08090F;
        background-image: 
            radial-gradient(circle at 15% 15%, rgba(124, 58, 237, 0.15) 0%, transparent 45%),
            radial-gradient(circle at 85% 30%, rgba(236, 72, 153, 0.12) 0%, transparent 40%),
            radial-gradient(circle at 50% 85%, rgba(6, 182, 212, 0.08) 0%, transparent 50%);
        background-attachment: fixed;
        color: #F8FAFC;
    }
    
    /* Header do Streamlit */
    header[data-testid="stHeader"] {
        background: rgba(8, 9, 15, 0.75) !important;
        backdrop-filter: blur(16px) !important;
    }
    
    /* Espaçamento do container principal */
    .block-container {
        padding-top: 4.5rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1440px;
    }
    
    /* Barra Lateral Escura e Minimalista */
    [data-testid="stSidebar"] {
        background-color: rgba(12, 14, 24, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
        padding-top: 1rem;
    }
    
    /* Animações Principais */
    @keyframes floatSlow {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-6px); }
    }
    @keyframes shimmerButton {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes popBounceEffect {
        0%, 100% { transform: scale(1.12); }
        50% { transform: scale(0.96); }
    }
    @keyframes fadeSoftEffect {
        0%, 100% { opacity: 0.25; transform: translateY(3px); }
        50% { opacity: 1; transform: translateY(0); }
    }
    @keyframes videoLightsFlow {
        0% { background-position: 0% 0%; filter: brightness(0.95) contrast(1.1); }
        25% { background-position: 50% 100%; filter: brightness(1.2) contrast(1.2); }
        50% { background-position: 100% 50%; filter: brightness(0.9) contrast(1.1); }
        75% { background-position: 50% 0%; filter: brightness(1.25) contrast(1.25); }
        100% { background-position: 0% 0%; filter: brightness(0.95) contrast(1.1); }
    }
    @keyframes rotateVinyl {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    @keyframes videoTimelineBar {
        0% { width: 0%; }
        100% { width: 100%; }
    }
    @keyframes pulseGamerGlow {
        0%, 100% { opacity: 0.3; transform: scale(1); }
        50% { opacity: 0.65; transform: scale(1.08); }
    }
    
    .anim-pop { animation: popBounceEffect 0.75s infinite ease-in-out; }
    .anim-fade { animation: fadeSoftEffect 1.1s infinite ease-in-out; }
    
    /* Topbar Navigation */
    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 20px;
        background: rgba(18, 21, 38, 0.65);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        margin-bottom: 22px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }
    .brand-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 1.25rem;
        font-weight: 900;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, #FFFFFF 0%, #E2E8F0 60%, #A78BFA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .brand-icon {
        background: linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%);
        width: 34px;
        height: 34px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.15rem;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
    }
    
    /* Stepper Bar 3 Etapas */
    .stepper-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 8px;
        margin-bottom: 22px;
        flex-wrap: nowrap;
    }
    .step-item {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 7px 16px;
        border-radius: 25px;
        font-weight: 700;
        font-size: 0.82rem;
        white-space: nowrap;
        transition: all 0.3s ease;
    }
    .step-active {
        background: linear-gradient(135deg, rgba(124, 58, 237, 0.35) 0%, rgba(236, 72, 153, 0.25) 100%);
        border: 1px solid #8B5CF6;
        color: #FFFFFF;
        box-shadow: 0 4px 18px rgba(139, 92, 246, 0.3);
    }
    .step-inactive {
        background: rgba(18, 21, 38, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.06);
        color: #64748B;
    }
    .step-done {
        color: #10B981 !important;
        border: 1px solid rgba(16, 185, 129, 0.4) !important;
        background: rgba(16, 185, 129, 0.12) !important;
    }
    
    /* Cards Modernos no Estilo Glassmorphism 2.0 */
    .saas-card {
        background: linear-gradient(135deg, rgba(18, 21, 38, 0.75) 0%, rgba(12, 14, 26, 0.85) 100%);
        backdrop-filter: blur(24px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 18px;
        padding: 18px 20px;
        margin-bottom: 16px;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }
    .saas-card:hover {
        border-color: rgba(139, 92, 246, 0.35);
        box-shadow: 0 14px 40px -10px rgba(139, 92, 246, 0.15);
        transform: translateY(-2px);
    }
    .saas-card-header {
        font-size: 1.02rem;
        font-weight: 800;
        color: #F8FAFC;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 10px;
        letter-spacing: -0.2px;
    }
    .saas-card-header span {
        font-size: 1.15rem;
    }
    
    /* Input Box Estilo SaaS Futurista */
    .stTextInput > div > div > input {
        background-color: rgba(10, 12, 22, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.09) !important;
        border-radius: 14px !important;
        color: #FFFFFF !important;
        padding: 14px 18px !important;
        font-size: 0.96rem !important;
        transition: all 0.2s ease !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #8B5CF6 !important;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.35) !important;
        background-color: rgba(14, 16, 30, 0.95) !important;
    }
    
    /* Botões Modernos com Gradiente e Efeito Shimmer */
    .stButton > button {
        border-radius: 14px !important;
        font-weight: 800 !important;
        padding: 12px 24px !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        letter-spacing: -0.2px !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #7C3AED 0%, #A855F7 50%, #EC4899 100%) !important;
        background-size: 200% 200% !important;
        animation: shimmerButton 6s ease infinite !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4) !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 12px 35px rgba(124, 58, 237, 0.65) !important;
        transform: translateY(-2px) scale(1.01) !important;
    }
    .stButton > button:not([kind="primary"]) {
        background: rgba(19, 23, 41, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #E2E8F0 !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        background: rgba(30, 36, 64, 0.9) !important;
        border-color: #8B5CF6 !important;
        transform: translateY(-1px) !important;
    }
    
    /* Chips de Amostras / Presets */
    .sample-pill {
        display: inline-block;
        background: rgba(139, 92, 246, 0.08);
        border: 1px solid rgba(139, 92, 246, 0.25);
        color: #C4B5FD;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.76rem;
        font-weight: 700;
        margin: 4px 4px 4px 0;
        cursor: default;
    }
    
    /* Mockup do Smartphone (Proporção 9:16 com Animação Float) */
    .sub-phone-container {
        display: flex;
        justify-content: center;
        margin: 10px 0;
        animation: floatSlow 5s ease-in-out infinite;
    }
    .sub-phone-mockup {
        width: 190px;
        height: 338px; /* Exato 9:16 */
        background: #090B14;
        border: 3.5px solid #2F3554;
        border-radius: 28px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 16px 45px rgba(0, 0, 0, 0.85), 0 0 25px rgba(139, 92, 246, 0.2);
    }
    .phone-screen {
        width: 100%;
        height: 100%;
        position: relative;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 8px 6px;
        background: linear-gradient(135deg, #1E1B4B 0%, #311042 25%, #0B1528 50%, #4A0E4E 75%, #0F172A 100%);
        background-size: 300% 300%;
        animation: videoLightsFlow 8s ease infinite;
        overflow: hidden;
    }
    .video-timeline {
        position: absolute;
        bottom: 0;
        left: 0;
        height: 3px;
        background: linear-gradient(90deg, #8B5CF6, #EC4899);
        box-shadow: 0 0 8px #EC4899;
        animation: videoTimelineBar 10s linear infinite;
        z-index: 10;
    }
    .vinyl-disc {
        width: 22px;
        height: 22px;
        border-radius: 50%;
        background: radial-gradient(circle, #EC4899 25%, #111 26%, #111 60%, #444 61%, #111 100%);
        border: 1.5px solid rgba(255, 255, 255, 0.4);
        animation: rotateVinyl 4s linear infinite;
        box-shadow: 0 0 8px rgba(236, 72, 153, 0.5);
    }
    .gamer-bg-glow {
        position: absolute;
        top: 35%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.45) 0%, rgba(236, 72, 153, 0.25) 50%, transparent 80%);
        animation: pulseGamerGlow 4s ease-in-out infinite;
        pointer-events: none;
    }
    .phone-notch {
        width: 44px;
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
        bottom: 45px;
        display: flex;
        flex-direction: column;
        gap: 8px;
        z-index: 4;
        font-size: 0.62rem;
        color: rgba(255, 255, 255, 0.75);
        text-align: center;
    }
    .sub-preview-content {
        position: absolute;
        bottom: 64px;
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
    
    /* Mockup Widescreen (16:9 com Animação Float) */
    .sub-wide-container {
        display: flex;
        justify-content: center;
        margin: 10px 0;
        animation: floatSlow 5s ease-in-out infinite;
    }
    .sub-wide-mockup {
        width: 100%;
        max-width: 320px;
        height: 180px; /* 16:9 */
        background: #090B14;
        border: 3.5px solid #2F3554;
        border-radius: 16px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 16px 45px rgba(0, 0, 0, 0.85), 0 0 25px rgba(139, 92, 246, 0.2);
    }
    .wide-screen {
        width: 100%;
        height: 100%;
        position: relative;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 10px 14px;
        background: linear-gradient(135deg, #1E1B4B 0%, #311042 25%, #0B1528 50%, #4A0E4E 75%, #0F172A 100%);
        background-size: 300% 300%;
        animation: videoLightsFlow 8s ease infinite;
        overflow: hidden;
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
        bottom: 24px;
        left: 10px;
        right: 10px;
        text-align: center;
        z-index: 5;
    }

    /* Cards de Corte Individual (Página 3) */
    .hotpeak-item {
        background: linear-gradient(135deg, rgba(18, 21, 38, 0.8) 0%, rgba(12, 14, 26, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 16px;
        margin-bottom: 20px;
        transition: all 0.25s ease;
    }
    .hotpeak-item:hover {
        border-color: #8B5CF6;
        box-shadow: 0 10px 30px rgba(139, 92, 246, 0.25);
    }
    .score-chip {
        background: linear-gradient(135deg, #EC4899 0%, #8B5CF6 100%);
        color: white;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 800;
        font-size: 0.78rem;
        box-shadow: 0 2px 10px rgba(236, 72, 153, 0.3);
    }
    .time-chip {
        background: rgba(255, 255, 255, 0.06);
        color: #94A3B8;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.78rem;
    }
    .hook-badge-box {
        background: rgba(236, 72, 153, 0.09);
        border-left: 3px solid #EC4899;
        padding: 8px 12px;
        border-radius: 8px;
        margin: 10px 0;
        font-size: 0.85rem;
        color: #FCE7F3;
        font-style: italic;
    }

    /* Elementos Nativos com Tema Escuro Consistente */
    [data-testid="stSelectbox"] div[data-baseweb="select"] {
        background-color: rgba(10, 12, 22, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.09) !important;
        border-radius: 12px !important;
        color: #FFFFFF !important;
    }
    [data-testid="stSelectbox"] div[data-baseweb="select"] * {
        color: #FFFFFF !important;
    }
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[data-baseweb="menu"] {
        background-color: #121528 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
    }
    li[data-baseweb="menu-item"] {
        color: #FFFFFF !important;
        background-color: #121528 !important;
    }
    li[data-baseweb="menu-item"]:hover {
        background-color: #201D3D !important;
        color: #C4B5FD !important;
    }
    label, [data-testid="stWidgetLabel"] p {
        color: #CBD5E1 !important;
        font-weight: 600 !important;
    }
    textarea {
        background-color: rgba(10, 12, 22, 0.85) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.09) !important;
        border-radius: 12px !important;
    }
    div[data-testid="stExpander"] {
        background-color: rgba(15, 17, 30, 0.75) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
    }
    div[data-testid="stExpander"] details summary {
        color: #E2E8F0 !important;
    }
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
        background: rgba(139, 92, 246, 0.15);
        color: #FFFFFF;
        border-left: 3px solid #8B5CF6;
    }

    /* OTIMIZAÇÕES RESPONSIVAS ESPECÍFICAS PARA SMARTPHONES / CELULARES */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 4.2rem !important;
            padding-bottom: 2rem !important;
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }
        .top-nav {
            padding: 10px 14px !important;
            margin-bottom: 14px !important;
            border-radius: 14px !important;
        }
        .brand-logo {
            font-size: 1.05rem !important;
            gap: 8px !important;
        }
        .brand-icon {
            width: 30px !important;
            height: 30px !important;
            font-size: 1rem !important;
            border-radius: 8px !important;
        }
        .stepper-container {
            gap: 4px !important;
            margin-bottom: 14px !important;
        }
        .step-item {
            padding: 5px 8px !important;
            font-size: 0.68rem !important;
            border-radius: 16px !important;
        }
        .saas-card {
            padding: 14px 14px !important;
            margin-bottom: 12px !important;
            border-radius: 14px !important;
        }
        .saas-card-header {
            font-size: 0.92rem !important;
            margin-bottom: 8px !important;
            gap: 6px !important;
        }
        .sample-pill {
            padding: 3px 8px !important;
            font-size: 0.7rem !important;
            margin: 2px 2px 2px 0 !important;
        }
        .sub-phone-container {
            margin: 8px 0 !important;
            animation: none !important;
        }
        .sub-phone-mockup {
            width: 145px !important;
            height: 258px !important;
            border-width: 2.5px !important;
            border-radius: 20px !important;
        }
        .sub-wide-container {
            margin: 8px 0 !important;
            animation: none !important;
        }
        .sub-wide-mockup {
            max-width: 250px !important;
            height: 140px !important;
            border-width: 2.5px !important;
            border-radius: 12px !important;
        }
        .sub-preview-content {
            bottom: 48px !important;
            left: 4px !important;
            right: 20px !important;
        }
        .sub-preview-text {
            font-size: 10px !important;
        }
        .phone-side-icons {
            bottom: 35px !important;
            right: 4px !important;
            gap: 5px !important;
            font-size: 0.52rem !important;
        }
        .stButton > button {
            padding: 10px 16px !important;
            font-size: 0.88rem !important;
            border-radius: 12px !important;
        }
        .stTextInput > div > div > input {
            padding: 10px 14px !important;
            font-size: 0.88rem !important;
            border-radius: 10px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Barra Lateral de Navegação
with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:20px;">
        <div class="brand-icon">⚡</div>
        <div style="font-size:1.25rem; font-weight:900; color:#FFFFFF; letter-spacing:-0.5px;">GravitiCuts AI</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="nav-item nav-item-active">📊 Studio de Cortes</div>
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

# Top Bar (Header Minimalista e Moderno)
st.markdown("""
<div class="top-nav">
    <div class="brand-logo">
        <div class="brand-icon">⚡</div>
        <span>GravitiCuts AI Studio</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Inicialização do Session State
if "current_step" not in st.session_state:
    st.session_state.current_step = 1
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False
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
if "cfg_num_cuts" not in st.session_state:
    st.session_state.cfg_num_cuts = 3
if "cfg_min_sec" not in st.session_state:
    st.session_state.cfg_min_sec = 30
if "cfg_max_sec" not in st.session_state:
    st.session_state.cfg_max_sec = 60
if "cfg_custom_prompt" not in st.session_state:
    st.session_state.cfg_custom_prompt = ""

# Stepper Dinâmico em 3 Etapas
def render_stepper(step):
    s1_class = "step-active" if step == 1 else "step-done"
    s1_icon = "1️⃣" if step == 1 else "✅"
    s1_text = "1. Inserir Link" if step == 1 else "1. Link OK"
    
    s2_class = "step-active" if step == 2 else ("step-done" if step > 2 else "step-inactive")
    s2_icon = "2️⃣" if step <= 2 else "✅"
    s2_text = "2. Formato & Estilo"
    
    s3_class = "step-active" if step == 3 else "step-inactive"
    s3_icon = "3️⃣" if step == 3 else "✨"
    s3_text = "3. Cortes & Exportação"
    
    sep1 = "#8B5CF6" if step > 1 else "rgba(255,255,255,0.15)"
    sep2 = "#8B5CF6" if step > 2 else "rgba(255,255,255,0.15)"
    
    return f"""
    <div class="stepper-container">
        <div class="step-item {s1_class}"><span>{s1_icon}</span> {s1_text}</div>
        <div style="color:{sep1}; font-weight:900;">──</div>
        <div class="step-item {s2_class}"><span>{s2_icon}</span> {s2_text}</div>
        <div style="color:{sep2}; font-weight:900;">──</div>
        <div class="step-item {s3_class}"><span>{s3_icon}</span> {s3_text}</div>
    </div>
    """

st.markdown(render_stepper(st.session_state.current_step), unsafe_allow_html=True)

# ==============================================================================
# ETAPA 1: INSERIR LINK DO YOUTUBE (TELA 1)
# ==============================================================================
if st.session_state.current_step == 1:
    st.markdown("""
    <div class="saas-card" style="border: 1px solid rgba(139, 92, 246, 0.35); background: linear-gradient(135deg, rgba(25, 20, 50, 0.75) 0%, rgba(13, 15, 28, 0.85) 100%);">
        <div class="saas-card-header" style="margin-bottom:0px;">
            <span>🔗</span> Insira o Link do Vídeo do YouTube
        </div>
    </div>
    """, unsafe_allow_html=True)

    url_input = st.text_input(
        "URL do YouTube",
        value=st.session_state.cfg_url,
        placeholder="Ex: https://www.youtube.com/watch?v=... ou https://youtu.be/...",
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)

    # Botão de Avanço da Etapa 1 para a Etapa 2
    btn_load_video = st.button("🚀 Carregar Vídeo & Escolher Formato ➔", type="primary", use_container_width=True)

    if btn_load_video:
        if not url_input.strip():
            st.warning("⚠️ Por favor, insira o link do vídeo do YouTube.")
        else:
            video_id = extract_video_id(url_input)
            if not video_id:
                st.error("❌ Não foi possível identificar o vídeo. Verifique a URL.")
            else:
                with st.spinner("📥 Coletando metadados do vídeo..."):
                    try:
                        v_info = get_video_info(url_input)
                    except Exception:
                        v_info = {"title": "Vídeo do YouTube", "duration": 0, "thumbnail": "", "channel": "Canal YouTube"}
                    
                    st.session_state.cfg_url = url_input
                    st.session_state.cfg_video_id = video_id
                    st.session_state.video_info = v_info
                    st.session_state.current_step = 2
                    st.rerun()

# ==============================================================================
# ETAPA 2: CONFIGURAR FORMATO, PROPORÇÃO & LEGENDAS (TELA 2)
# ==============================================================================
elif st.session_state.current_step == 2:
    # Resumo do Vídeo Carregado com opção de trocar
    if st.session_state.video_info:
        v_info = st.session_state.video_info
        col_v1, col_v2 = st.columns([4, 1])
        with col_v1:
            st.markdown(f"""
            <div class="saas-card" style="display:flex; gap:16px; align-items:center; padding:12px 16px; margin-bottom:16px;">
                <img src="{v_info.get('thumbnail', '')}" style="width:90px; height:52px; border-radius:8px; object-fit:cover;">
                <div>
                    <div style="font-weight:800; font-size:0.95rem; color:#FFFFFF; line-height:1.2;">{v_info.get('title', 'Vídeo Selecionado')}</div>
                    <div style="color:#94A3B8; font-size:0.78rem;">👤 {v_info.get('channel', '')} &nbsp;|&nbsp; ⏱️ {format_timestamp(v_info.get('duration', 0))}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_v2:
            if st.button("⬅️ Trocar Vídeo", use_container_width=True):
                st.session_state.current_step = 1
                st.rerun()

    # Grid Responsivo: Configurações à Esquerda e Prévia Interativa à Direita
    col_cfg1, col_cfg2 = st.columns([1.15, 0.85], gap="large")

    with col_cfg1:
        # 1. Proporção & Formato
        with st.container():
            st.markdown("""
            <div class="saas-card">
                <div class="saas-card-header">📱 Formato & Proporção do Vídeo</div>
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
                <div class="saas-card-header">💬 Legendas Dinâmicas nos Cortes</div>
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
                <div style="background:rgba(15,17,32,0.85); border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:14px; color:#94A3B8; font-size:0.86rem; margin-top:8px;">
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
                num_cuts = st.number_input("Cortes (Máx: 5)", min_value=1, max_value=5, value=st.session_state.cfg_num_cuts, help="Limite fixado em até 5 cortes por análise")
            with col_d2:
                min_sec = st.number_input("Mín (s)", min_value=15, max_value=60, value=st.session_state.cfg_min_sec)
            with col_d3:
                max_sec = st.number_input("Máx (s)", min_value=30, max_value=180, value=st.session_state.cfg_max_sec)

        # 4. Instrução Personalizada com IA
        with st.container():
            st.markdown("""
            <div class="saas-card">
                <div class="saas-card-header">🎯 Instrução Personalizada para a IA (Opcional)</div>
            </div>
            """, unsafe_allow_html=True)
            custom_prompt = st.text_input(
                "Prompt Personalizado",
                value=st.session_state.cfg_custom_prompt,
                placeholder="Ex: Quero cortes com jogadas incríveis, explicações claras, momentos engraçados...",
                label_visibility="collapsed"
            )
            st.markdown("""
            <div>
                <span class="sample-pill">🔥 Melhores Ganchos</span>
                <span class="sample-pill">😂 Momentos Engraçados</span>
                <span class="sample-pill">📊 Insights & Dados</span>
                <span class="sample-pill">🎮 Melhores Jogadas</span>
            </div>
            """, unsafe_allow_html=True)

    with col_cfg2:
        # Coluna Dinâmica de Prévia com Efeito Flutuante e Iluminação Neon
        is_widescreen = (video_style == "original" or "16:9" in str(video_style))
        preview_title = "Prévia em Tempo Real (16:9)" if is_widescreen else "Prévia em Tempo Real (9:16)"
        preview_icon = "🖥️" if is_widescreen else "📱"
        
        with st.container():
            st.markdown(f"""
            <div class="saas-card" style="text-align:center; padding:16px 12px; border: 1px solid rgba(139, 92, 246, 0.25);">
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
                        f'<div class="video-timeline"></div>'
                        f'<div class="gamer-bg-glow"></div>'
                        f'<div style="display:flex; justify-content:space-between; align-items:center; z-index:5;">'
                        f'<div class="wide-badge-tag">🖥️ 16:9 Widescreen Preview</div>'
                        f'<div style="font-size:0.6rem; color:#94A3B8;">🔴 1080p60</div>'
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
                        f'<div class="video-timeline"></div>'
                        f'<div class="gamer-bg-glow"></div>'
                        f'<div>'
                        f'<div class="phone-notch"></div>'
                        f'<div class="phone-badge-tag">📱 9:16 Shorts Preview</div>'
                        f'</div>'
                        f'<div class="phone-side-icons">'
                        f'<div>❤️<br><span style="font-size:0.52rem;">42K</span></div>'
                        f'<div>💬<br><span style="font-size:0.52rem;">1.2K</span></div>'
                        f'<div>↗️<br><span style="font-size:0.52rem;">Share</span></div>'
                        f'<div style="margin-top:2px;"><div class="vinyl-disc"></div></div>'
                        f'</div>'
                        f'<div style="position:absolute; bottom:14px; left:8px; display:flex; align-items:center; gap:5px; z-index:6;">'
                        f'<div style="width:14px; height:14px; border-radius:50%; background:linear-gradient(135deg, #8B5CF6, #EC4899); border:1px solid #FFF; font-size:0.5rem; display:flex; align-items:center; justify-content:center;">⚡</div>'
                        f'<span style="font-size:0.55rem; font-weight:800; color:#FFF;">@gravitiGames</span>'
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
                        f'<div class="video-timeline"></div>'
                        f'<div class="gamer-bg-glow"></div>'
                        f'<div style="display:flex; justify-content:space-between; align-items:center; z-index:5;">'
                        f'<div class="wide-badge-tag">🖥️ 16:9 Widescreen</div>'
                        f'<div style="font-size:0.6rem; color:#10B981;">● Vídeo Limpo</div>'
                        f'</div>'
                        f'<div class="wide-preview-content">'
                        f'<div style="color:rgba(255,255,255,0.45); font-size:0.85rem; font-weight:800; letter-spacing:0.5px;">'
                        f'🎬 SEM LEGENDAS'
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
                        f'<div class="video-timeline"></div>'
                        f'<div class="gamer-bg-glow"></div>'
                        f'<div>'
                        f'<div class="phone-notch"></div>'
                        f'<div class="phone-badge-tag">📱 9:16 Shorts</div>'
                        f'</div>'
                        f'<div class="phone-side-icons">'
                        f'<div>❤️<br><span style="font-size:0.52rem;">42K</span></div>'
                        f'<div>💬<br><span style="font-size:0.52rem;">1.2K</span></div>'
                        f'<div>↗️<br><span style="font-size:0.52rem;">Share</span></div>'
                        f'<div style="margin-top:2px;"><div class="vinyl-disc"></div></div>'
                        f'</div>'
                        f'<div style="position:absolute; bottom:14px; left:8px; display:flex; align-items:center; gap:5px; z-index:6;">'
                        f'<div style="width:14px; height:14px; border-radius:50%; background:linear-gradient(135deg, #8B5CF6, #EC4899); border:1px solid #FFF; font-size:0.5rem; display:flex; align-items:center; justify-content:center;">⚡</div>'
                        f'<span style="font-size:0.55rem; font-weight:800; color:#FFF;">@gravitiGames</span>'
                        f'</div>'
                        f'<div class="sub-preview-content">'
                        f'<div style="color:rgba(255,255,255,0.45); font-size:0.85rem; font-weight:800; letter-spacing:0.5px;">'
                        f'🎬 SEM LEGENDAS'
                        f'</div>'
                        f'</div>'
                        f'</div>'
                        f'</div>'
                        f'</div>'
                    )
                st.markdown(mockup_html, unsafe_allow_html=True)
                st.caption(f"<div style='text-align:center; color:#94A3B8; margin-top:8px;'>✨ Prévia do seu corte {('16:9' if is_widescreen else '9:16')} sem legendas (vídeo original limpo).</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Botão Principal de Ação (Avança para a Etapa 3)
    analyze_btn = st.button("⚡ GERAR CORTES VIRAIS COM GRAVITICUTS IA", type="primary", use_container_width=True)

    if analyze_btn:
        # Salva todas as opções no session_state
        st.session_state.cfg_video_style = video_style
        st.session_state.cfg_enable_subtitles = enable_subtitles
        st.session_state.cfg_sub_style = sub_style
        st.session_state.cfg_sub_anim = sub_anim
        st.session_state.cfg_sub_fontsize = sub_fontsize
        st.session_state.cfg_num_cuts = min(5, max(1, int(num_cuts)))
        st.session_state.cfg_min_sec = min_sec
        st.session_state.cfg_max_sec = max_sec
        st.session_state.cfg_custom_prompt = custom_prompt
        
        # Ativa processamento e transita IMEDIATAMENTE para a Etapa 3
        st.session_state.is_processing = True
        st.session_state.cuts = []
        st.session_state.current_step = 3
        st.rerun()

# ==============================================================================
# ETAPA 3: PROCESSAR, VISUALIZAR & EXPORTAR (TELA 3)
# ==============================================================================
elif st.session_state.current_step == 3:
    # SE ESTIVER PROCESSANDO: EXIBE EXCLUSIVAMENTE A TELA DE CARREGAMENTO
    if st.session_state.get("is_processing", False):
        col_c1, col_c2 = st.columns([1, 4])
        with col_c1:
            if st.button("⬅️ Cancelar", use_container_width=True):
                st.session_state.is_processing = False
                st.session_state.current_step = 2
                st.rerun()
                
        status_slot = st.empty()
        progress_bar = st.progress(25)
        
        # Etapa 1/3 (Metadados)
        status_slot.markdown("""
        <div class="saas-card" style="text-align:center; padding:40px 20px; border:1px solid #7C3AED; box-shadow:0 0 35px rgba(124,58,237,0.25);">
            <div style="font-size:3rem; margin-bottom:12px;">📥⚡</div>
            <div style="font-size:1.4rem; font-weight:900; color:#FFFFFF; margin-bottom:6px; letter-spacing:-0.5px;">Etapa 1/3: Sincronizando Vídeo</div>
            <div style="color:#C4B5FD; font-size:0.92rem;">Verificando integridade e canal do YouTube...</div>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.video_info:
            try:
                video_info = get_video_info(st.session_state.cfg_url)
                st.session_state.video_info = video_info
            except Exception:
                video_info = {"title": "Vídeo do YouTube", "duration": 0, "thumbnail": "", "channel": ""}
                st.session_state.video_info = video_info
        else:
            video_info = st.session_state.video_info

        # Etapa 2/3 (Transcrição)
        progress_bar.progress(55)
        status_slot.markdown("""
        <div class="saas-card" style="text-align:center; padding:40px 20px; border:1px solid #7C3AED; box-shadow:0 0 35px rgba(124,58,237,0.25);">
            <div style="font-size:3rem; margin-bottom:12px;">📝⚡</div>
            <div style="font-size:1.4rem; font-weight:900; color:#FFFFFF; margin-bottom:6px; letter-spacing:-0.5px;">Etapa 2/3: Extraindo Transcrição e Timestamps</div>
            <div style="color:#C4B5FD; font-size:0.92rem;">Lendo e sincronizando as falas com precisão milimétrica...</div>
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

        # Etapa 3/3 (IA Gemini Minerando Momentos Virais)
        progress_bar.progress(85)
        status_slot.markdown("""
        <div class="saas-card" style="text-align:center; padding:40px 20px; border:1px solid #7C3AED; box-shadow:0 0 35px rgba(124,58,237,0.25);">
            <div style="font-size:3rem; margin-bottom:12px;">🧠⚡</div>
            <div style="font-size:1.4rem; font-weight:900; color:#FFFFFF; margin-bottom:6px; letter-spacing:-0.5px;">Etapa 3/3: GravitiCuts IA Minerando Picos Virais</div>
            <div style="color:#C4B5FD; font-size:0.92rem;">Calculando HotPeaks de retenção, ganchos magnéticos e viralidade...</div>
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

    # SE O PROCESSAMENTO ESTIVER CONCLUÍDO: MOSTRA O FEED DE CORTES DA ETAPA 3
    else:
        # Barra de Ações Superior
        col_nav1, col_nav2, col_nav3 = st.columns([1, 1.2, 3])
        with col_nav1:
            if st.button("⬅️ Novo Vídeo", use_container_width=True):
                st.session_state.current_step = 1
                st.session_state.is_processing = False
                st.session_state.cuts = []
                st.session_state.video_info = None
                st.session_state.downloaded_video_path = None
                st.rerun()
        with col_nav2:
            if st.button("⚙️ Alterar Formato", use_container_width=True):
                st.session_state.current_step = 2
                st.rerun()
        with col_nav3:
            st.markdown(f"""
            <div style="background:rgba(19, 21, 38, 0.75); border:1px solid rgba(255,255,255,0.08); padding:8px 16px; border-radius:12px; display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:900; color:#C4B5FD; font-size:0.92rem;">🔥 {len(st.session_state.cuts)} Cortes Virais Gerados</span>
                <span style="font-size:0.8rem; color:#94A3B8;">Formato: <strong style="color:#F1F5F9;">{st.session_state.cfg_video_style}</strong> | Legendas: <strong style="color:#F1F5F9;">{'Sim' if st.session_state.cfg_enable_subtitles else 'Não'}</strong></span>
            </div>
            """, unsafe_allow_html=True)

        # Card de Resumo do Vídeo Original
        if st.session_state.video_info:
            v_info = st.session_state.video_info
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="saas-card" style="display:flex; gap:20px; align-items:center;">
                <img src="{v_info.get('thumbnail', '')}" style="width:140px; border-radius:10px; object-fit:cover; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
                <div>
                    <div style="font-weight:900; font-size:1.15rem; color:#FFFFFF; margin-bottom:4px; letter-spacing:-0.3px;">{v_info.get('title', '')}</div>
                    <div style="color:#94A3B8; font-size:0.85rem;">👤 Canal: <strong style="color:#E2E8F0;">{v_info.get('channel', 'Desconhecido')}</strong> &nbsp;|&nbsp; ⏱️ Duração: <strong style="color:#E2E8F0;">{format_timestamp(v_info.get('duration', 0))}</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Grid de Cortes Sugeridos (Estilo Feed de Cortes Moderno)
        if st.session_state.cuts:
            current_video_id = extract_video_id(st.session_state.cfg_url)
            grid_columns = 3 # 3 colunas padrão no PC
            
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
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                                    <span class="score-chip">🔥 PICO VIRAL {cut['score']}%</span>
                                    <span class="time-chip">⏱️ {format_timestamp(cut['start_time'])} - {format_timestamp(cut['end_time'])} ({cut['duration']}s)</span>
                                </div>
                                <div style="font-weight:900; font-size:1.05rem; color:#FFFFFF; line-height:1.35; margin-bottom:10px; letter-spacing:-0.2px;">
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

                            # Exibição do vídeo pronto e botão de download
                            if f"ready_video_{cut_idx}" in st.session_state:
                                video_file_path = st.session_state[f"ready_video_{cut_idx}"]
                                if os.path.exists(video_file_path):
                                    st.markdown("##### 📱 Corte Finalizado:")
                                    st.video(video_file_path)
                                    with open(video_file_path, "rb") as file_data:
                                        st.download_button(
                                            label=f"⬇️ Baixar Corte #{cut_idx+1} (.mp4)",
                                            data=file_data,
                                            file_name=os.path.basename(video_file_path),
                                            mime="video/mp4",
                                            key=f"dl_{cut_idx}",
                                            use_container_width=True
                                        )
                            
                            st.markdown("<br>", unsafe_allow_html=True)
