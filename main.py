import os
import time
import requests
from flask import Flask

# Configuração do Servidor Web do Flask (Mantém o Render ativo 24h grátis)
app = Flask(__name__)

@app.route('/')
def home():
    return "Robô de Futebol Ativo e a Funcionar!"

# Credenciais do Telegram (As mesmas que já estão a funcionar)
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

# Mensagem de teste inicial para confirmar que ligou
enviar_telegram("🤖 *Robô Atualizado!* Pronto para buscar Gols (75'-90') e Escanteios (80'+).")

def monitorar_jogos():
    try:
        # Nota: Se estiver a usar uma API pública ou gratuita de futebol (como API-Football ou similar),
        # coloque aqui o link e os parâmetros corretos. 
        # Este bloco simula a estrutura que vai varrer os jogos ao vivo:
        
        url_api = "https://sua-api-de-futebol.com/live" # Substitua pelo endpoint da sua API gratuita
        headers = {"X-RapidAPI-Key": "sua_chave_aqui"} # Se aplicável
        
        # Exemplo estrutural de leitura de dados ao vivo:
        # resposta = requests.get(url_api, headers=headers, timeout=10)
        # jogos = resposta.json().get('response', [])
        
        jogos = [] # Lista de exemplo (substitua pelos dados reais da sua API)
        
        for jogo in jogos:
            # Recolha dos dados da partida em tempo real
            minuto = jogo.get('fixture', {}).get('status', {}).get('elapsed', 0)
            nome_casa = jogo.get('teams', {}).get('home', {}).get('name', 'Casa')
            nome_fora = jogo.get('teams', {}).get('away', {}).get('name', 'Fora')
            
            gols_casa = jogo.get('goals', {}).get('home', 0)
            gols_fora = jogo.get('goals', {}).get('away', 0)
            
            cantos_casa = jogo.get('statistics', {}).get('corners_home', 0)
            cantos_fora = jogo.get('statistics', {}).get('corners_away', 0)
            
            nome_jogo = f"{nome_casa} vs {nome_fora}"
            placar = f"{gols_casa} x {gols_fora}"

            # ----------------------------------------------------
            # ESTRATÉGIA 1: GOL TARDIO (Minuto 75 ao 90+) - Qualquer Placar
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
        print("Aviso na verificação dos jogos (continuando o ciclo):", e)

def rodar_loop_em_segundo_plano():
    import threading
    def loop():
        while True:
            monitorar_jogos()
            # Pausa de 60 segundos para não exceder limites de requisições gratuitas
            time.sleep(60)
    
    t = threading.Thread(target=loop)
    t.daemon = True
    t.start()

# Inicia a thread do robô para rodar junto com o servidor Flask
rodar_loop_em_segundo_plano()

if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)
