import requests
import time
from datetime import datetime, timedelta

TOKEN = "TOKEN"
CHAT_ID = "CHAT_ID"

def telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url,data={"chat_id":CHAT_ID,"text":msg})

def tum_coinler():
    url="https://api.btcturk.com/api/v2/ticker"
    return requests.get(url).json()["data"]

son_mesaj = datetime.now()

telegram("🤖 BOT AKTİF (test modu)")

while True:

    coinler=tum_coinler()

    firsatlar=[]

    for coin in coinler:

        pair=coin["pair"]
        fiyat=float(coin["last"])
        degisim=float(coin["dailyPercent"])

        # fırsat mantığı
        if degisim > 1:

            firsatlar.append((pair,fiyat,degisim))

    if len(firsatlar)>0:

        eniyi=max(firsatlar,key=lambda x:x[2])

        telegram(

f"""
🚀 FIRSAT

Coin: {eniyi[0]}

Fiyat: {eniyi[1]}

24s değişim: %{round(eniyi[2],2)}

Yükseliş devam edebilir
"""
)

    # düşüş uyarısı

    dusenler=[]

    for coin in coinler:

        pair=coin["pair"]
        degisim=float(coin["dailyPercent"])

        if degisim < -2:

            dusenler.append((pair,degisim))

    if len(dusenler)>0:

        en_kotu=min(dusenler,key=lambda x:x[1])

        telegram(

f"""
🚨 DÜŞÜŞ UYARISI

Coin: {en_kotu[0]}

24s değişim: %{round(en_kotu[1],2)}

Düşüş devam edebilir
"""
)

    # 2 saatte bir rapor

    simdi=datetime.now()

    if simdi-son_mesaj > timedelta(hours=2):

        telegram("📊 BOT ÇALIŞIYOR ve piyasayı tarıyor")

        son_mesaj=simdi

    time.sleep(900)
