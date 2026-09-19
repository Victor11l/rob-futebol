import os
import time
import requests
from flask import Flask
import threading

# --- CONFIGURAÇÕES ---
TELEGRAM_TOKEN = "8691804127:AAEBA2d0ufb2hm5-Zeinr0a0lXzygH8zxrM"
CHAT_ID = "5662043242"
RAPIDAPI_KEY = "74d2422d0fmshc41b54343716963p1aa78djsn567458323ada"

# Configuração do Servidor Web do Flask (Mantém o Render ativo 24h grátis)
app = Flask(__name__)

@app.route('/')
def home():
    return "Robô de Futebol Ativo e a Funcionar!"

# Para evitar alertas repetidos do mesmo jogo
jogos_alertados = set()

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    try:
        resposta = requests.post(url, json=payload)
        print("RESPOSTA DO TELEGRAM:", resposta.status_code, resposta.text)
    except Exception as e:
        print(f"Erro ao enviar mensagem no Telegram: {e}")

# Mensagem de teste instantânea para confirmar que ligou
enviar_telegram("🤖 *Robô Atualizado e Conectado!* Monitorando Gols (75'+) e Cantos (80'+).")

def verificar_jogos():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    headers = {
        "X-RapidAPI-Key": "74d2422d0fmshc41b54343716963p1a-a78djsn567458323ada",
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    params = {"live": "all"} # Busca todos os jogos ao vivo

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        dados = response.json()

        if "response" not in dados:
            return

        for partida in dados["response"]:
            fixture_id = partida["fixture"]["id"]
            minuto = partida["fixture"]["status"]["elapsed"]
            time_casa = partida["teams"]["home"]["name"]
            time_fora = partida["teams"]["away"]["name"]
            
            gols_casa = partida["goals"]["home"] if partida["goals"]["home"] is not None else 0
            gols_fora = partida["goals"]["away"] if partida["goals"]["away"] is not None else 0

            # Evita processar jogos sem minutos definidos (intervalo, adiados, etc)
            if minuto is None:
                continue

            placar = f"{gols_casa} x {gols_fora}"

            # -------------------------------------------------------------------------
            # CRITÉRIO 1: GOLS DOS 75' ATÉ O FIM (Qualquer Placar)
            # -------------------------------------------------------------------------
            if 75 <= minuto <= 95:
                chave_alerta = f"{fixture_id}_gols_75"
                if chave_alerta not in jogos_alertados:
                    msg = (
                        f"⚽ *ALERTA: GOL TARDIO (75'+)*\n\n"
                        f"🎮 *{time_casa}* {placar} *{time_fora}*\n"
                        f"⏱ *Minuto:* {minuto}'\n"
                        f"💡 *Sugestão:* Jogo na reta final, buscar gol (qualquer placar)!"
                    )
                    enviar_telegram(msg)
                    jogos_alertados.add(chave_alerta)

            # -------------------------------------------------------------------------
            # CRITÉRIO 2: ESCANTEIOS DOS 80' ATÉ O FIM (Pressão Final)
            # -------------------------------------------------------------------------
            if minuto >= 80:
                chave_alerta = f"{fixture_id}_cantos_80"
                if chave_alerta not in jogos_alertados:
                    msg = (
                        f"🚩 *ALERTA: ESCANTEIOS / PRESSÃO (80'+)*\n\n"
                        f"🎮 *{time_casa}* {placar} *{time_fora}*\n"
                        f"⏱ *Minuto:* {minuto}'\n"
                        f"💡 *Sugestão:* Pressão total no fim, buscar +1 ou +2 cantos!"
                    )
                    enviar_telegram(msg)
                    jogos_alertados.add(chave_alerta)

    except Exception as e:
        print(f"Erro ao consultar API: {e}")

def rodar_loop_em_segundo_plano():
    def loop():
        while True:
            verificar_jogos()
            # Pausa de 60 segundos entre cada verificação para atualizar os minutos em tempo real
            time.sleep(60)
            
    t = threading.Thread(target=loop)
    t.daemon = True
    t.start()

# Inicia a thread em segundo plano junto com o servidor web
rodar_loop_em_segundo_plano()

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)
