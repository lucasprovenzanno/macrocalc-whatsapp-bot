# METAS DO SEU MACROCALC
METAS = {
    "treino": {
        "calorias": 2750,
        "proteina": 205,
        "carboidratos": 290,
        "gorduras": 80
    },
    "descanso": {
        "calorias": 2350,
        "proteina": 210,
        "carboidratos": 165,
        "gorduras": 90
    }
}

# PROMPT PARA KIMI
SYSTEM_PROMPT = """Você é um nutricionista esportivo especializado em recomposição corporal.

REGRAS:
1. Analise a refeição descrita
2. Estime macros (calorias, proteina, carboidratos, gorduras)
3. Compare com as metas do usuário
4. Responda em PORTUGUÊS, formato curto e direto

FORMATO DA RESPOSTA:
📊 [Refeição]: X kcal | P: Xg | C: Xg | G: Xg
📈 Progresso: X% cal | X% prot | X% carb
💡 Dica: [sugestão breve]"""
