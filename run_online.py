import os
import sys
import subprocess
import re
import time
import urllib.request
import webbrowser

BANNER = """
======================================================================
         🚀 GRAVITICUTS AI - SERVIDOR ONLINE INICIADO COM SUCESSO!
======================================================================

  ✅ Servidor Streamlit Local: Ativo (Porta 8501)
  ✅ Túnel Cloudflare Seguro: Conectado (Zero Erro 403 do YouTube)
  ✅ Processamento: Rodando no seu hardware com IP residencial!

======================================================================
  🔗 SEU LINK PÚBLICO PARA ACESSAR NO CELULAR OU QUALQUER LUGAR:
======================================================================

     👉 {public_url} 👈

  *(O link foi copiado automaticamente para a sua Área de Transferência!)*
======================================================================
  📱 Dicas de uso:
  - Abra o link acima no navegador do seu celular.
  - Envie para seus amigos no WhatsApp para eles testarem!
  - Todos os downloads do YouTube funcionarão 100% sem erro 403.
  - Para encerrar o servidor, basta fechar esta janela do terminal.
======================================================================
"""

def ensure_cloudflared() -> str:
    exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cloudflared.exe")
    if not os.path.exists(exe_path):
        print("📥 Baixando executável do Cloudflare Tunnel (cloudflared.exe)...")
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        urllib.request.urlretrieve(url, exe_path)
        print("✅ Download concluído!")
    return exe_path

def copy_to_clipboard(text: str):
    try:
        if sys.platform == "win32":
            subprocess.run(["clip"], input=text.strip().encode("utf-8"), check=True)
    except Exception:
        pass

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    cloudflared_path = ensure_cloudflared()

    print("🚀 1/2 Iniciando Streamlit local...")
    streamlit_cmd = [
        sys.executable,
        "-m", "streamlit", "run", "app.py",
        "--server.headless", "true",
        "--server.port", "8501"
    ]
    st_proc = subprocess.Popen(
        streamlit_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    print("🌐 2/2 Abrindo túnel público seguro com a Cloudflare...")
    cf_cmd = [
        cloudflared_path,
        "tunnel",
        "--url", "http://localhost:8501"
    ]
    cf_proc = subprocess.Popen(
        cf_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    public_url = None
    start_time = time.time()
    while time.time() - start_time < 30:
        line = cf_proc.stdout.readline()
        if not line:
            time.sleep(0.1)
            continue
        match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
        if match:
            public_url = match.group(0)
            break

    if not public_url:
        print("⚠️ Não foi possível capturar o link automaticamente em 30 segundos.")
        print("Verifique se o Cloudflare conseguiu se conectar à internet.")
        st_proc.terminate()
        cf_proc.terminate()
        return

    # Copia o link para a área de transferência do Windows
    copy_to_clipboard(public_url)

    # Limpa a tela e exibe o banner destacado
    os.system("cls" if os.name == "nt" else "clear")
    print(BANNER.format(public_url=public_url))

    # Abre automaticamente no navegador do usuário
    try:
        webbrowser.open(public_url)
    except Exception:
        pass

    try:
        # Mantém ambos os processos vivos
        while True:
            time.sleep(1)
            if st_proc.poll() is not None or cf_proc.poll() is not None:
                break
    except KeyboardInterrupt:
        print("\n🛑 Encerrando servidor e túnel...")
    finally:
        st_proc.terminate()
        cf_proc.terminate()
        print("✅ Servidor finalizado com sucesso.")

if __name__ == "__main__":
    main()
