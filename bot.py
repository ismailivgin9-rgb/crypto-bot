import requests
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

TOKEN = "TOKEN"
CHAT_ID = "CHAT_ID"

SCALPING = True

def telegram(msg):

    url=f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(url,data={"chat_id":CHAT_ID,"text":msg})


def telegram_grafik(symbol):

    url=f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=30"

    data=requests.get(url).json()

    fiyatlar=[float(x[4]) for x in data]

    plt.figure()

    plt.plot(fiyatlar)

    dosya=f"{symbol}.png"

    plt.savefig(dosya)

    plt.close()

    url2=f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    requests.post(url2,files={"photo":open(dosya,"rb")},data={"chat_id":CHAT_ID})


def binance():

    url="https://api.binance.com/api/v3/ticker/24hr"

    return requests.get(url).json()


telegram("🤖 FULL AI BOT AKTİF")

son_rapor=datetime.now()

gunluk_potansiyel=0

while True:

    data=binance()

    adaylar=[]
    scalpler=[]
    pumplar=[]
    dususler=[]

    for coin in data:

        symbol=coin["symbol"]

        fiyat=float(coin["lastPrice"])

        degisim=float(coin["priceChangePercent"])

        hacim=float(coin["quoteVolume"])

        yuksek=float(coin["highPrice"])

        dusuk=float(coin["lowPrice"])

        if hacim < 2000000:
            continue


        volatilite=(yuksek-dusuk)/dusuk

        skor=0

        yorum=[]


        if degisim > 2:

            skor+=2
            yorum.append("trend yukarı")


        if volatilite > 0.04:

            skor+=2
            yorum.append("volatilite yüksek")


        if hacim > 5000000:

            skor+=2
            yorum.append("hacim güçlü")


        if skor >=4:

            adaylar.append((symbol,fiyat,degisim,skor,", ".join(yorum)))

            gunluk_potansiyel+=degisim


        if SCALPING and 0.5 < degisim < 3 and volatilite > 0.02:

            scalpler.append((symbol,fiyat,degisim))


        # pump tespiti

        if degisim > 6 and hacim > 8000000:

            pumplar.append((symbol,fiyat,degisim))


        # dump tespiti

        if degisim < -5:

            dususler.append((symbol,fiyat,degisim))


    if len(adaylar)>0:

        eniyi=max(adaylar,key=lambda x:x[3])

        telegram(f"""

🔥 EN ÇOK ARTABİLİR

Coin: {eniyi[0]}

Fiyat: {eniyi[1]}

24s değişim: %{round(eniyi[2],2)}

AI analiz:
{eniyi[4]}

""")

        telegram_grafik(eniyi[0])


    if len(scalpler)>0:

        s=max(scalpler,key=lambda x:x[2])

        telegram(f"""

⚡ SCALPING FIRSATI

Coin: {s[0]}

kısa vadeli hareket bekleniyor

""")

        telegram_grafik(s[0])


    if len(pumplar)>0:

        p=max(pumplar,key=lambda x:x[2])

        telegram(f"""

🚀 PUMP TESPİT

Coin: {p[0]}

%{round(p[2],2)} yükseliş

hacim artışı var

""")

        telegram_grafik(p[0])


    if len(dususler)>0:

        d=min(dususler,key=lambda x:x[2])

        telegram(f"""

🚨 DÜŞÜŞ UYARISI

Coin: {d[0]}

%{round(d[2],2)} düşüş

risk yüksek

""")

        telegram_grafik(d[0])


    simdi=datetime.now()

    if simdi-son_rapor > timedelta(hours=24):

        telegram(f"""

📊 GÜNLÜK POTANSİYEL

Toplam fırsat kazanç ihtimali:

%{round(gunluk_potansiyel,2)}

""")

        gunluk_potansiyel=0

        son_rapor=simdi


    time.sleep(600)
