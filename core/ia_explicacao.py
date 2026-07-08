import os
 
from huggingface_hub import InferenceClient
 
 
client = InferenceClient(
    api_key=os.getenv("HF_TOKEN")
)

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

    try:
        resposta = client.chat.completions.create(
            model=os.getenv("HF_MODEL_EXPLICACAO"),
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=120,
        )
 
        return resposta.choices[0].message.content
 
    except Exception:
        return "Não foi possível gerar a explicação do plano agora. Tente novamente em instantes."