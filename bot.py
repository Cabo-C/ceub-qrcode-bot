import requests
import schedule
import time
import base64
import logging
import pytz
import os
from datetime import datetime
from bs4 import BeautifulSoup

# -----------------------------------------
# VARIÁVEIS DE AMBIENTE
# ----------------------------------------
LOGIN = os.getenv("LOGIN")
SENHA = os.getenv("SENHA")
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL_LOGIN = "https://aluno.ceub.br/Conta/LogOn"
URL_QR = "https://ea.uniceub.br/Home/GetQrCode"

session = requests.Session()

# -----------------------------------------
# LOG BONITO
# -----------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="👉 %(asctime)s | %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("bot")

TZ = pytz.timezone("America/Sao_Paulo")
def agora():
    return datetime.now(TZ).strftime("%H:%M:%S")

def avisar(msg):
    requests.get(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        params={"chat_id": CHAT_ID, "text": msg}
    )

# Teste inicial
avisar("🤖 Bot iniciou no Railway!")

# -----------------------------------------
# LOGIN
# -----------------------------------------
def fazer_login():
    log.info("🔐 Fazendo login...")

    r = session.get(URL_LOGIN)
    soup = BeautifulSoup(r.text, "html.parser")
    token = soup.find("input", {"name": "__RequestVerificationToken"})
    token = token["value"] if token else ""

    payload = {
        "__RequestVerificationToken": token,
        "hidLoginEDS": "",
        "coAcesso": LOGIN,
        "coSenha": SENHA,
        "icManterConectado": "false",
        "ReCaptchaToken": ""
    }

    resp = session.post(URL_LOGIN, data=payload)

    if "Espaço Aluno" in resp.text:
        log.info("✅ Login OK")
        return True

    log.error("❌ Login falhou")
    return False

# -----------------------------------------
# PEGAR QR CODE
# -----------------------------------------
def pegar_qrcode():
    log.info("🔄 Baixando QR Code...")

    resp = session.get(URL_QR)
    if resp.status_code != 200:
        log.error("❌ Erro ao buscar QR")
        return None

    data = resp.json()
    if "QRCode" not in data:
        log.error("❌ QR não encontrado")
        return None

    b64 = data["QRCode"].replace("data:image/jpeg;base64,", "")
    return base64.b64decode(b64)

# -----------------------------------------
# ENVIAR FOTO
# -----------------------------------------
def enviar_qr(imagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    files = {"photo": ("qr.jpg", imagem)}
    data = {"chat_id": CHAT_ID}
    r = requests.post(url, files=files, data=data)
    return r.json().get("result", {}).get("message_id")

def apagar_msg(msg_id):
    url = f"https://api.telegram.org/bot{TOKEN}/deleteMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "message_id": msg_id})

# -----------------------------------------
# TAREFAS
# -----------------------------------------
ultima_msg = None

def tarefa_diaria():
    global ultima_msg
    log.info("▶️ Executando tarefa diária")

    if not fazer_login():
        return

    img = pegar_qrcode()
    if img:
        ultima_msg = enviar_qr(img)

def apagar_diario():
    global ultima_msg
    if ultima_msg:
        apagar_msg(ultima_msg)
        ultima_msg = None

# HORÁRIOS BRASIL
schedule.every().day.at("12:00").do(tarefa_diaria)
schedule.every().day.at("22:00").do(apagar_diario)

log.info("🟣 Bot rodando no Railway...")

# LOOP FINAL
while True:
    schedule.run_pending()
    time.sleep(1)

