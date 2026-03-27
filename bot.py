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

def telegram(msg):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

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

    if rsi<35:

        skor+=2

        yorum.append("RSI dip seviyede")

    if macd>0:

        skor+=2

        yorum.append("Trend yukarı")

    if fiyat<alt:

        skor+=2

        yorum.append("Alt bant temas")

    ort=df["close"].mean()

    if fiyat>ort:

        skor+=1

    return skor,fiyat,volatilite,", ".join(yorum)

gecmis={}

alinanlar={}

gunluk_sinyal=0

basarili=0

toplam_kar=0

son_rapor=datetime.now()

son_tahmin=datetime.now()

son_balina=datetime.now()

son_haber=datetime.now()

son_dusus=datetime.now()

telegram("🤖 FULL AI BOT AKTİF")

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

        if len(gecmis[pair])>60:

            gecmis[pair].pop(0)

        if len(gecmis[pair])>30:

            skor,fiyat,volatilite,yorum=analiz(gecmis[pair])

            if volatilite>0.06:

                continue

            if skor>en_skor:

                en_skor=skor

                en_iyi=(pair,fiyat,skor,yorum)

    if en_iyi and en_skor>=4:

        coin,fiyat,skor,yorum=en_iyi

        if SCALPING_MOD:

            hedef=fiyat*1.02

            sure="30-90 dk"

        else:

            hedef=fiyat*1.05

            sure="2-6 saat"

        alinanlar[coin]=hedef

        gunluk_sinyal+=1

        telegram(

f"""

🚀 AI FIRSAT

Coin: {coin}

🟢 ALIŞ: {round(fiyat,4)}

🎯 HEDEF: {round(hedef,4)}

📈 KAR: %{round(((hedef-fiyat)/fiyat)*100,2)}

⏰ Süre: {sure}

🧠 AI Yorum:
{yorum}

🛡 Risk: düşük

📊 Güç: {skor}/10

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

Fiyat hedefe ulaştı

İşlem tamam

"""
)

                del alinanlar[pair]

    simdi=datetime.now()

    # günlük rapor

    if simdi-son_rapor>timedelta(hours=24):

        telegram(

f"""

📊 GÜNLÜK RAPOR

Sinyal: {gunluk_sinyal}

Başarılı: {basarili}

Bot aktif çalışıyor

"""
)

        gunluk_sinyal=0

        basarili=0

        son_rapor=simdi

    # en çok artabilecek coin tahmini

    if simdi-son_tahmin>timedelta(hours=4):

        aday=None

        en_skor2=0

        for pair in gecmis:

            if len(gecmis[pair])>30:

                skor,fiyat,volatilite,yorum=analiz(gecmis[pair])

                if skor>en_skor2:

                    en_skor2=skor

                    aday=(pair,skor,yorum)

        if aday:

            telegram(

f"""

🔥 YÜKSELME ADAYI

Coin: {aday[0]}

Potansiyel yüksek

Sebep:
{aday[2]}

"""
)

        son_tahmin=simdi

    # balina hareketi

    if simdi-son_balina>timedelta(minutes=30):

        for pair in gecmis:

            f=gecmis[pair]

            if len(f)>8:

                degisim=(f[-1]-f[-5])/f[-5]

                if abs(degisim)>0.03:

                    telegram(

f"""

🐋 BALİNA HAREKETİ

Coin: {pair}

Ani fiyat değişimi

%{round(degisim*100,2)}

"""
)

        son_balina=simdi

    # haber yorumu

    if simdi-son_haber>timedelta(hours=6):

        telegram(

"""

📰 PİYASA HABER

BTC hareketleri piyasayı etkileyebilir

Volatilite artabilir

"""
)

        son_haber=simdi

    # düşüş erken uyarı

    if simdi-son_dusus>timedelta(minutes=20):

        for pair in gecmis:

            f=gecmis[pair]

            if len(f)>8:

                degisim=(f[-1]-f[-6])/f[-6]

                if degisim<-0.025:

                    telegram(

f"""

🚨 ERKEN DÜŞÜŞ

Coin: {pair}

Hızlı düşüş algılandı

%{round(degisim*100,2)}

Risk artıyor

"""
)

        son_dusus=simdi

    time.sleep(180)