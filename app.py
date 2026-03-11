from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import os
from config import METAS, SYSTEM_PROMPT
from datetime import datetime

app = Flask(__name__)

# Banco simples em memória (depois trocamos por SQLite)
usuarios = {}

def get_kimi_response(mensagem, metas):
    """Chama API da Kimi"""
    api_key = os.getenv('KIMI_API_KEY')
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "kimi-latest",
        "messages": [
            {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nMetas atuais: {metas}"},
            {"role": "user", "content": mensagem}
        ],
        "temperature": 0.3
    }
    
    try:
        response = requests.post(
            "https://api.moonshot.cn/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ Erro ao consultar Kimi: {str(e)}"

@app.route("/webhook", methods=['POST'])
def webhook():
    # Dados do Twilio
    numero = request.form.get('From')
    msg = request.form.get('Body', '').strip().lower()
    
    # Inicializa usuário se não existe
    if numero not in usuarios:
        usuarios[numero] = {
            "modo": "treino",  # padrão
            "refeicoes": [],
            "data": datetime.now().date()
        }
    
    user = usuarios[numero]
    
    # Reseta se mudou de dia
    if datetime.now().date() != user['data']:
        user['refeicoes'] = []
        user['data'] = datetime.now().date()
    
    # COMANDOS
    if msg == "treino":
        user['modo'] = "treino"
        resposta = "🏋️ Modo TREINO ativado!\n" \
                   f"Metas: {METAS['treino']['calorias']}kcal | " \
                   f"P:{METAS['treino']['proteina']}g | " \
                   f"C:{METAS['treino']['carboidratos']}g"
    
    elif msg == "descanso":
        user['modo'] = "descanso"
        resposta = "🛋️ Modo DESCANSO ativado!\n" \
                   f"Metas: {METAS['descanso']['calorias']}kcal | " \
                   f"P:{METAS['descanso']['proteina']}g | " \
                   f"C:{METAS['descanso']['carboidratos']}g"
    
    elif msg == "status":
        resposta = get_status(user)
    
    elif msg == "ajuda":
        resposta = """🤖 COMANDOS:
• TREINO - Ativa modo treino
• DESCANSO - Ativa modo descanso  
• STATUS - Ver progresso do dia
• [descreva refeição] - Analisa macros

Ex: "Almoço 300g lasanha\""""
    
    else:
        # Analisa refeição com Kimi
        metas = METAS[user['modo']]
        resposta = get_kimi_response(request.form.get('Body'), metas)
        
        # Salva refeição (simplificado)
        user['refeicoes'].append({
            'hora': datetime.now(),
            'descricao': request.form.get('Body'),
            'resposta': resposta
        })
    
    # Envia resposta WhatsApp
    twilio_resp = MessagingResponse()
    twilio_resp.message(resposta)
    return str(twilio_resp)

def get_status(user):
    """Mostra progresso do dia"""
    metas = METAS[user['modo']]
    qtd = len(user['refeicoes'])
    return f"""📊 PROGRESSO DE HOJE ({user['modo'].upper()})

🍽️ Refeições registradas: {qtd}

Metas:
🔥 {metas['calorias']}kcal
💪 {metas['proteina']}g prot
🍚 {metas['carboidratos']}g carb

💡 Envie uma refeição para análise!"""

if __name__ == "__main__":
    app.run(debug=True, port=5000)
