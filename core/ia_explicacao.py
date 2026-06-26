import requests


def gerar_explicacao(plano, objetivo, peso, atividade):

    prompt = f"""
    Você é um coach nutricional.

    Explique em no máximo 80 palavras por que o plano {plano}
    foi recomendado para um usuário com:

    Objetivo: {objetivo}
    Peso: {peso}kg
    Atividade: {atividade}

    Regras:
    - Seja direto
    - Não explique o que é o plano
    - Não faça listas
    - Não dê introduções
    - Não use avisos médicos
    - Não diga "eu sou uma IA"
    - Foque apenas no motivo da escolha
    - Responda em um único parágrafo
    """

    response = requests.post(
        "http://localhost:1234/v1/chat/completions",
        json={
            "model": "gemma-3-1b-it",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4,
            "max_tokens": 120
        }
    )

    resposta = response.json()

    return resposta["choices"][0]["message"]["content"]