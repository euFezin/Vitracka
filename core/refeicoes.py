import os

from huggingface_hub import InferenceClient


client = InferenceClient(
    api_key=os.getenv("HF_TOKEN")
)

REFEICOES = ['café da manhã', 'almoço', 'lanche da tarde', 'jantar']

SYSTEM_PROMPT = """Você é Vix, nutricionista do app Vitracka, especialista em hipertrofia e performance.

Sua tarefa é sugerir alimentos para UMA refeição específica, respeitando os macros do plano do usuário.

Responda APENAS com uma lista simples de alimentos com quantidade, no formato:
- [quantidade] [alimento] ([calorias aproximadas] kcal)

Máximo de 5 itens. Sem introdução, sem explicação, sem texto extra. Apenas a lista.
"""


def gerar_refeicao(refeicao, plano):
    prompt = f"""
Plano do usuário:
- Calorias totais: {plano['calorias']} kcal/dia
- Proteína: {plano['proteina']}g
- Carboidratos: {plano['carboidratos']}g
- Gordura: {plano['gordura']}g

Sugira alimentos para o {refeicao} desse usuário.
Distribua aproximadamente 25% das calorias totais nessa refeição.
"""

    try:
        resposta = client.chat.completions.create(
            model=os.getenv("HF_MODEL_REFEICOES"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=500,
        )

        texto = (resposta.choices[0].message.content or "").strip()

        if not texto:
            raise ValueError("O modelo retornou uma resposta vazia.")

        return texto

    except Exception as e:
        print(f"[ERRO] Falha ao gerar refeição: {e}")
        return "Não foi possível gerar a sugestão de refeição agora. Tente novamente em instantes."


def gerar_todas_refeicoes(plano):
    return {r: gerar_refeicao(r, plano) for r in REFEICOES}