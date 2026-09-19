import os
import time
import requests
from flask import Flask

app = Flask(__name__)

# Suas credenciais do Telegram
TELEGRAM_TOKEN = "8699095311:AAGm16_21HwBFNp-T0BQLQSp7yorKR2VkA4"
CHAT_ID = "5662043242"

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    try:
        resposta = requests.post(url, json=payload)
        print("RESPOSTA DO TELEGRAM:", resposta.status_code, resposta.text)
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

# DISPARO IMEDIATO NA IMPORTAÇÃO (Assim que o Python lê o ficheiro)
print("A enviar mensagem de arranque...")
enviar_telegram("🤖 *Robô Ligado!* O sistema arrancou com sucesso no Render.")

@app.route('/')
def home():
    return "Robô de Futebol Ativo!"

def monitorar_jogos():
    try:
        url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
        querystring = {"live": "all"}
        headers = {
            "X-RapidAPI-Key": "COLOQUE_A_SUA_RAPIDAPI_KEY_AQUI",
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }
        
        resposta = requests.get(url, headers=headers, params=querystring, timeout=15)
        dados = resposta.json()
        jogos = dados.get('response', [])
        
        for jogo in jogos:
            fixture = jogo.get('fixture', {})
            minuto = fixture.get('status', {}).get('elapsed', 0)
            
            teams = jogo.get('teams', {})
            nome_casa = teams.get('home', {}).get('name', 'Casa')
            nome_fora = teams.get('away', {}).get('name', 'Fora')
            
            goals = jogo.get('goals', {})
            gols_casa = goals.get('home') or 0
            gols_fora = goals.get('away') or 0

            statistics = jogo.get('statistics', [])
            cantos_casa = 0
            cantos_fora = 0
            
            for stat_team in statistics:
                team_name = stat_team.get('team', {}).get('name')
                for s in stat_team.get('statistics', []):
                    if s.get('type') == 'Corner Kicks':
                        val = s.get('value')
                        if val is not None:
                            if team_name == nome_casa:
                                cantos_casa = int(val)
                            elif team_name == nome_fora:
                                cantos_fora = int(val)

            nome_jogo = f"{nome_casa} vs {nome_fora}"
            placar = f"{gols_casa} x {gols_fora}"

            # ESTRATÉGIA 1: GOL TARDIO (75' a 95')
            if 75 <= minuto <= 95:
                enviar_telegram(f"⚽ *ALERTA DE GOL TARDIO*\n🎮 Jogo: {nome_jogo}\n⏱️ Minuto: {minuto}'\n📊 Placar: {placar}")

            # ESTRATÉGIA 2: ESCANTEIOS DE PRESSÃO (80'+)
            if minuto >= 80:
                enviar_telegram(f"🚩 *ALERTA DE ESCANTEIOS*\n🎮 Jogo: {nome_jogo}\n⏱️ Minuto: {minuto}'\n📐 Cantos: {cantos_casa} a {cantos_fora}")

    except Exception as e:
        print("Erro na monitorização:", e)

def iniciar_loop():
    import threading
    def loop():
        while True:
            monitorar_jogos()
            time.sleep(60)
    t = threading.Thread(target=loop)
    t.daemon = True
    t.start()

# Inicia a thread do robô
iniciar_loop()

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)
