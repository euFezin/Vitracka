import os

from huggingface_hub import InferenceClient


SYSTEM_PROMPT = """Você é Vix, um coach nutricional do app Vitracka, especialista em hipertrofia, emagrecimento e performance.

Responda APENAS perguntas relacionadas a:
- Nutrição, dieta e alimentação
- Macronutrientes (proteína, carboidrato, gordura)
- Calorias e metabolismo
- Suplementação
- Estratégias de bulking, cutting e manutenção
- Hidratação e hábitos alimentares

Se a pergunta não tiver relação com esses temas, responda exatamente:
"Só consigo ajudar com dúvidas sobre nutrição e dieta. Tem alguma pergunta sobre sua alimentação?"

Regras de resposta:
- Seja direto e prático
- Máximo de 3 parágrafos curtos
- Sem listas longas
- Sem avisos médicos genéricos
- Sem dizer que é uma IA
"""

client = InferenceClient(
    api_key=os.getenv("HF_TOKEN")
)


def gerar_resposta_chat(historico):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *historico
    ]

    try:
        resposta = client.chat.completions.create(
            model=os.getenv("HF_MODEL"),
            messages=messages,
            temperature=0.5,
            max_tokens=300,
        )
        
        return resposta.choices[0].message.content
    
    except Exception:
        return "Desculpe, não consegui gerar uma resposta no momento. Por favor, tente novamente mais tarde."