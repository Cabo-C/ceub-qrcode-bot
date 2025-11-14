import requests
import schedule
import time
import base64
from datetime import datetime
import pytz
# -----------------------------------------
# CONFIGURAÇÕES (use variáveis de ambiente no Railway)
# -----------------------------------------
LOGIN = ""       # seu RA / email
SENHA = ""
TELEGRAM_TOKEN = ""
CHAT_ID = ""

URL_LOGIN = "https://aluno.ceub.br/Conta/LogOn"
URL_QR = "https://ea.uniceub.br/Home/GetQrCode"

session = requests.Session()

TZ = pytz.timezone("America/Sao_Paulo")

def agora():
    return datetime.now(TZ).strftime("%H:%M:%S")

def tarefa():
    print(f"[{agora()}] Executando tarefa...")

schedule.every().day.at("08:30").do(tarefa)

while True:
    schedule.run_pending()
    time.sleep(1)

# -----------------------------------------
# LOGIN
# -----------------------------------------
def fazer_login():
    print("🔐 Fazendo login...")

    # Primeiro acesso para pegar o token do formulário
    r = session.get(URL_LOGIN)
    if r.status_code != 200:
        print("❌ Erro ao acessar página de login")
        return False

    # Extrai o token hidden (__RequestVerificationToken)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, "html.parser")
    token = soup.find("input", {"name": "__RequestVerificationToken"})
    token = token["value"] if token else ""

    payload = {
        "__RequestVerificationToken": token,
        "hidLoginEDS": "",
        "coAcesso": LOGIN,
        "coSenha": SENHA,
        "icManterConectado": "false",
        "ReCaptchaToken": ""   # vazio como você confirmou
    }

    resp = session.post(URL_LOGIN, data=payload, allow_redirects=True)

    if "Espaço Aluno" in resp.text or resp.status_code == 200:
        print("✅ Login realizado com sucesso!")
        return True

    print("❌ Falha no login.")
    return False


# -----------------------------------------
# PEGAR QR CODE
# -----------------------------------------
def pegar_qrcode():
    print("🔄 Baixando QR Code...")

    resp = session.get(URL_QR)

    if resp.status_code != 200:
        print("❌ Erro ao buscar QR Code")
        return None

    data = resp.json()

    if "QRCode" not in data:
        print("❌ JSON não contém 'QRCode'")
        return None

    base64_img = data["QRCode"].replace("data:image/jpeg;base64,", "")
    return base64.b64decode(base64_img)


# -----------------------------------------
# ENVIAR PARA TELEGRAM
# -----------------------------------------
def enviar_telegram(imagem_bytes):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    files = {"photo": ("qrcode.jpg", imagem_bytes)}
    data = {"chat_id": CHAT_ID}

    r = requests.post(url, files=files, data=data)
    print("📨 Mensagem enviada!")
    return r.json().get("result", {}).get("message_id")


# -----------------------------------------
# APAGAR MENSAGEM
# -----------------------------------------
def apagar_mensagem(message_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "message_id": message_id})
    print("🗑️ Mensagem apagada!")


# -----------------------------------------
# JOB DIÁRIO
# -----------------------------------------
ultima_msg = None

def tarefa_diaria():
    global ultima_msg

    print("\n=== EXECUTANDO TAREFA DIÁRIA ===")

    if not fazer_login():
        return

    qr = pegar_qrcode()
    if qr:
        ultima_msg = enviar_telegram(qr)


def apagar_diario():
    global ultima_msg
    if ultima_msg:
        apagar_mensagem(ultima_msg)
        ultima_msg = None


# HORÁRIOS
schedule.every().day.at("12:00").do(tarefa_diaria)
schedule.every().day.at("22:00").do(apagar_diario)


# LOOP
print("🟣 Bot rodando no Railway...")
while True:
    schedule.run_pending()
    time.sleep(1)

