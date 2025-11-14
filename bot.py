import time
import base64
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

# -----------------------------------------
LOGIN = ""
SENHA = ""

TELEGRAM_TOKEN = ""
CHAT_ID = ""

URL_LOGIN = "https://aluno.ceub.br/Conta/LogOn"


# -----------------------------------------
# ENVIAR FOTO PARA TELEGRAM
# -----------------------------------------
def enviar_telegram(imagem_bytes):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"

    files = {
        "photo": ("qrcode.png", imagem_bytes)
    }
    data = {
        "chat_id": CHAT_ID
    }

    requests.post(url, files=files, data=data)


# -----------------------------------------
# INICIAR SELENIUM
# -----------------------------------------
options = Options()
options.add_argument("--headless=new")  # roda sem abrir janela – se quiser ver, remova essa linha
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(URL_LOGIN)
time.sleep(2)

# -----------------------------------------
# FAZER LOGIN
# -----------------------------------------
driver.find_element(By.ID, "coAcesso").send_keys(LOGIN)
driver.find_element(By.ID, "coSenha").send_keys(SENHA)
driver.find_element(By.ID, "btn-login").click()
time.sleep(4)

# ----------

