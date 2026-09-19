import threading
import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Online!", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Inicia o servidor web em segundo plano para responder ao Render
threading.Thread(target=run_web, daemon=True).start()

import requests
import time

TELEGRAM_TOKEN = "8699095311:AAGml6_21HwBFNp-T0BQLQSp7yorKR2VkA4"
CHAT_ID = "5662043242"
RAPIDAPI_KEY = "74d2422d0fmshc41b54343716963p1aa78djsn567458323ada"

jogos_alertados = set()

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Erro ao enviar: {e}")

enviar_telegram("🤖 Teste de Notificação: O robô está ativo e a funcionar!")
        
def verificar_jogos():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    params = {"live": "all"}

    try:
        response = requests.get(url, headers=headers, params=params)
        dados = response.json()

        if "response" not in dados:
            return

        for partida in dados["response"]:
            fixture_id = partida["fixture"]["id"]
            minuto = partida["fixture"]["status"]["elapsed"]
            time_casa = partida["teams"]["home"]["name"]
            time_fora = partida["teams"]["away"]["name"]
            gols_casa = partida["goals"]["home"]
            gols_fora = partida["goals"]["away"]

            if minuto is None:
                continue

            # CRITÉRIO 1: Entrada +0.5 Gols (Placar 0x0 entre 70 e 80 minutos)
            if 70 <= minuto <= 80 and gols_casa == 0 and gols_fora == 0:
                if f"{fixture_id}_gols" not in jogos_alertados:
                    msg = f"🚨 *ALERTA +0.5 GOLS*\n\n⚽ {time_casa} 0 x 0 {time_fora}\n⏱ {minuto} min"
                    enviar_telegram(msg)
                    jogos_alertados.add(f"{fixture_id}_gols")

            # CRITÉRIO 2: Cantos Limite (Empate entre 80 e 87 minutos)
            elif 80 <= minuto <= 87 and gols_casa == gols_fora:
                if f"{fixture_id}_cantos" not in jogos_alertados:
                    msg = f"🚩 *ALERTA ESCANTEIOS*\n\n⚽ {time_casa} {gols_casa} x {gols_fora} {time_fora}\n⏱ {minuto} min"
                    enviar_telegram(msg)
                    jogos_alertados.add(f"{fixture_id}_cantos")

    except Exception as e:
        print(f"Erro na leitura: {e}")

# Consulta a cada 15 minutos (96 vezes ao dia para ficar 100% grátis)
while True:
    verificar_jogos()
    time.sleep(900)
enviar_telegram("🤖 Teste de Notificação: O robô está ativo e a funcionar!")
