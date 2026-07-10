import os

from huggingface_hub import InferenceClient


client = InferenceClient(
    api_key=os.getenv("HF_TOKEN")
)

SYSTEM_PROMPT = """Você é Vix, personal trainer do app Vitracka, especialista em musculação, hipertrofia, emagrecimento e performance.

Sua tarefa é montar um treino completo para o usuário.

Regras:

- Responda apenas com o treino.
- Organize por dias da semana.
- Para cada exercício informe séries e repetições.
- Não explique os exercícios.
- Não utilize Markdown complexo.
- Escreva em português.
"""

def gerar_treino(profile, goal):
    prompt = f"""
Crie um treino para o seguinte usuário.

Sexo: {profile.gender}
Idade: {profile.age}
Peso: {profile.weight} kg
Altura: {profile.height} cm
Nível de atividade: {profile.activity_level}

Objetivo:
{goal.objective}

Monte um treino completo dividido por dias.

Para cada exercício informe:

- exercício
- séries
- repetições

Retorne somente o treino.
"""

    try:
        resposta = client.chat.completions.create(
            model=os.getenv("HF_MODEL_TREINO"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
            max_tokens=900,
        )

        texto = (resposta.choices[0].message.content or "").strip()

        if not texto:
            raise ValueError("O modelo retornou uma resposta vazia.")

        return texto

    except Exception as e:
        print(e)
        raise