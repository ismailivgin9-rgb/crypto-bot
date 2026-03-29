import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands

TOKEN = "8704318933:AAEFNyA1_Jjs1L6CTEGk6Mk-XUGzU1SGM8Q"
CHAT_ID = "6209715808"

SCALPING_MOD = True

KAR_ORANI = 1.012
MIN_SINYAL = 3
MAX_VOLATILITE = 0.08

def telegram(msg):

    url=f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(url,data={"chat_id":CHAT_ID,"text":msg})

def tum_coinler():

    url="https://api.btcturk.com/api/v2/ticker"

    return requests.get(url).json()["data"]

def analiz(fiyatlar):

    df=pd.DataFrame(fiyatlar,columns=["close"])

    rsi=RSIIndicator(df["close"]).rsi().iloc[-1]

    macd=MACD(df["close"]).macd_diff().iloc[-1]

    bb=BollingerBands(df["close"])

    ust=bb.bollinger_hband().iloc[-1]

    alt=bb.bollinger_lband().iloc[-1]

    fiyat=df["close"].iloc[-1]

    volatilite=df["close"].pct_change().std()

    skor=0

    yorum=[]

    if rsi<40:
        skor+=2
        yorum.append("RSI düşük")

    if macd>0:
        skor+=2
        yorum.append("Trend yukarı")

    if fiyat<alt:
        skor+=2
        yorum.append("Alt bant")

    ort=df["close"].mean()

    if fiyat>ort:
        skor+=1

    return skor,fiyat,volatilite,", ".join(yorum)

gecmis={}
alinanlar={}

gunluk_sinyal=0
basarili=0

son_rapor=datetime.now()
son_tahmin=datetime.now()
son_balina=datetime.now()
son_dusus=datetime.now()

telegram("🤖 AI BOT AKTİF")

while True:

    coinler=tum_coinler()

    en_iyi=None
    en_skor=-999

    for coin in coinler:

        pair=coin["pair"]
        fiyat=float(coin["last"])

        if pair not in gecmis:
            gecmis[pair]=[]

        gecmis[pair].append(fiyat)

        if len(gecmis[pair])>50:
            gecmis[pair].pop(0)

        if len(gecmis[pair])>25:

            skor,fiyat,volatilite,yorum=analiz(gecmis[pair])

            if volatilite>MAX_VOLATILITE:
                continue

            if skor>en_skor:

                en_skor=skor
                en_iyi=(pair,fiyat,skor,yorum)

    if en_iyi and en_skor>=MIN_SINYAL:

        coin,fiyat,skor,yorum=en_iyi

        hedef=fiyat*KAR_ORANI

        alinanlar[coin]=hedef

        gunluk_sinyal+=1

        telegram(

f"""

🚀 AI FIRSAT

Coin: {coin}

Alış: {round(fiyat,4)}

Hedef: {round(hedef,4)}

Kar: %{round(((hedef-fiyat)/fiyat)*100,2)}

Sebep:
{yorum}

Risk: düşük

"""
)

    for coin in coinler:

        pair=coin["pair"]
        fiyat=float(coin["last"])

        if pair in alinanlar:

            hedef=alinanlar[pair]

            if fiyat>=hedef:

                basarili+=1

                telegram(

f"""

🔴 SAT

Coin: {pair}

Hedefe ulaştı

"""
)

                del alinanlar[pair]

    simdi=datetime.now()

    if simdi-son_rapor>timedelta(hours=24):

        telegram(

f"""

📊 RAPOR

Sinyal: {gunluk_sinyal}

Başarılı: {basarili}

"""
)

        gunluk_sinyal=0
        basarili=0

        son_rapor=simdi

    if simdi-son_tahmin>timedelta(hours=3):

        aday=None
        skor2=0

        for pair in gecmis:

            if len(gecmis[pair])>25:

                s,f,v,y=analiz(gecmis[pair])

                if s>skor2:

                    skor2=s
                    aday=(pair,y)

        if aday:

            telegram(

f"""

🔥 YÜKSELME ADAYI

Coin: {aday[0]}

Sebep:
{aday[1]}

"""
)

        son_tahmin=simdi

    if simdi-son_balina>timedelta(minutes=30):

        for pair in gecmis:

            f=gecmis[pair]

            if len(f)>10:

                degisim=(f[-1]-f[-5])/f[-5]

                if abs(degisim)>0.035:

                    telegram(

f"""

🐋 BALİNA HAREKETİ

Coin: {pair}

Değişim %{round(degisim*100,2)}

"""
)

        son_balina=simdi

    if simdi-son_dusus>timedelta(minutes=20):

        for pair in gecmis:

            f=gecmis[pair]

            if len(f)>8:

                degisim=(f[-1]-f[-6])/f[-6]

                if degisim<-0.03:

                    telegram(

f"""

🚨 DÜŞÜŞ UYARISI

Coin: {pair}

%{round(degisim*100,2)}

"""
)

        son_dusus=simdi

    time.sleep(120)
