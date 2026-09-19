import os
import time
import requests
from flask import Flask

# Configuração do Servidor Web do Flask (Mantém o Render ativo 24h grátis)
app = Flask(__name__)

@app.route('/')
def home():
    return "Robô de Futebol Ativo e a Funcionar!"

# Credenciais do Telegram
TELEGRAM_TOKEN = "8699095311:AAGm16_21HwBFNp-T0BQLQSp7yorKR2VkA4"
CHAT_ID = "5662043242"

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    try:
        resposta = requests.post(url, json=payload)
        print("RESPOSTA DO TELEGRAM:", resposta.status_code, resposta.text)
    except Exception as e:
        print("Erro ao enviar mensagem para o Telegram:", e)

# Mensagem de teste imediata para confirmar que ligou
enviar_telegram("🤖 *Robô Atualizado!* Pronto para buscar Gols (75'-90') e Cantos (80'+).")

def monitorar_jogos():
    try:
        # Configuração da API de Futebol (Exemplo padrão RapidAPI / API-Football)
        url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
        
        querystring = {"live": "all"}  # Puxa todos os jogos ao vivo do dia
        
        # ⚠️ Cole a sua chave do RapidAPI entre as aspas abaixo se ainda não tiver colocado:
        headers = {
            "X-RapidAPI-Key": "74d2422d0fmshc41b54343716963p1aa78djsn567458323ada",
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }
        
        # Faz o pedido HTTP para a API de futebol
        resposta = requests.get(url, headers=headers, params=querystring, timeout=15)
        dados = resposta.json()
        
        # Obtém a lista de jogos ao vivo
        jogos = dados.get('response', [])
        
        for jogo in jogos:
            # Extração dos dados do jogo em tempo real
            fixture = jogo.get('fixture', {})
            minuto = fixture.get('status', {}).get('elapsed', 0)
            
            teams = jogo.get('teams', {})
            nome_casa = teams.get('home', {}).get('name', 'Casa')
            nome_fora = teams.get('away', {}).get('name', 'Fora')
            
            goals = jogo.get('goals', {})
            gols_casa = goals.get('home', 0) if goals.get('home') is not None else 0
            gols_fora = goals.get('away', {}).get('name') and goals.get('away', 0) or 0
            # Ajuste seguro para gols
            gols_fora = goals.get('infer_away', 0) if 'infer_away' in goals else (goals.get('away') or 0)

            # Estatísticas (Cantos)
            statistics = jogo.get('statistics', [])
            cantos_casa = 0
            cantos_fora = 0
            
            # Percorre as estatísticas da API para achar os cantos (Corners)
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

            # ----------------------------------------------------
            # ESTRATÉGIA 1: GOL TARDIO (Minuto 75 ao 95) - Qualquer Placar
            # ----------------------------------------------------
            if 75 <= minuto <= 95:
                mensagem_gol = (
                    f"⚽ *ALERTA DE GOL TARDIO*\n"
                    f"🎮 Jogo: {nome_jogo}\n"
                    f"⏱️ Minuto: {minuto}'\n"
                    f"📊 Placar Atual: {placar}\n"
                    f"💡 *Estratégia:* Reta final, jogo aberto para buscar gol!"
                )
                enviar_telegram(mensagem_gol)

            # ----------------------------------------------------
            # ESTRATÉGIA 2: ESCANTEIOS DE PRESSÃO (Minuto 80 ao Fim)
            # ----------------------------------------------------
            if minuto >= 80:
                mensagem_cantos = (
                    f"🚩 *ALERTA DE PRESSÃO / ESCANTEIOS*\n"
                    f"🎮 Jogo: {nome_jogo}\n"
                    f"⏱️ Minuto: {minuto}'\n"
                    f"📐 Cantos Atuais: {cantos_casa} a {cantos_fora}\n"
                    f"💡 *Estratégia:* Pressão final, buscar +1 ou +2 cantos!"
                )
                enviar_telegram(mensagem_cantos)

    except Exception as e:
        print("Aviso na verificação dos jogos (o ciclo continua):", e)

def rodar_loop_em_segundo_plano():
    import threading
    def loop():
        while True:
            monitorar_jogos()
            # Pausa de 60 segundos entre cada consulta à API para poupar limite gratuito
            time.sleep(60)
    
    t = threading.Thread(target=loop)
    t.daemon = True
    t.start()

# Inicia a thread em segundo plano junto com o Flask
rodar_loop_em_segundo_plano()

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)
