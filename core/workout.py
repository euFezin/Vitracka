import os
import re

from huggingface_hub import InferenceClient


client = InferenceClient(
    api_key=os.getenv("HF_TOKEN")
)

DIAS_VALIDOS = {
    "segunda-feira", "terça-feira", "quarta-feira",
    "quinta-feira", "sexta-feira", "sábado", "domingo",
}

DIAS_POR_ATIVIDADE = {
    "sedentario": 3,
    "leve": 4,
    "moderado": 5,
    "intenso": 6,
}

SPLITS_SUGERIDOS = {
    3: ("Segunda-feira, Quarta-feira e Sexta-feira", "Full Body (corpo inteiro em cada sessão)"),
    4: ("Segunda-feira, Terça-feira, Quinta-feira e Sexta-feira", "Upper/Lower (superior e inferior alternados)"),
    5: ("Segunda-feira, Terça-feira, Quinta-feira, Sexta-feira e Sábado", "Push/Pull/Legs adaptado (empurrar, puxar, pernas)"),
    6: ("Segunda-feira, Terça-feira, Quarta-feira, Quinta-feira, Sexta-feira e Sábado", "Push/Pull/Legs (empurrar, puxar, pernas, repetindo o ciclo)"),
}

MIN_EXERCICIOS_POR_DIA = 4
MAX_EXERCICIOS_POR_DIA = 6

EXERCICIOS_VALIDOS = """
Agachamento livre, Agachamento no smith, Leg press, Cadeira extensora, Cadeira flexora,
Stiff, Levantamento terra, Afundo, Cadeira adutora, Cadeira abdutora, Panturrilha em pé,
Panturrilha sentado, Supino reto, Supino inclinado, Supino declinado, Crucifixo reto,
Crucifixo inclinado, Crossover, Flexão de braço, Desenvolvimento com halteres,
Desenvolvimento militar, Elevação lateral, Elevação frontal, Remada curvada, Remada cavalo,
Remada unilateral, Puxada frontal, Puxada aberta, Puxada fechada, Barra fixa, Remada baixa,
Rosca direta, Rosca alternada, Rosca martelo, Rosca scott, Tríceps corda, Tríceps testa,
Tríceps francês, Mergulho no banco, Abdominal supra, Abdominal infra, Prancha abdominal,
Elevação de pernas
"""

SYSTEM_PROMPT = f"""Você é Vix, personal trainer do app Vitracka, especialista em musculação, hipertrofia, emagrecimento e performance.

Sua tarefa é montar um treino completo para o usuário, seguindo EXATAMENTE este formato, sem nenhum texto adicional antes ou depois:

Segunda-feira
1. Nome do exercício - 3 séries x 10 repetições
2. Nome do exercício - 4 séries x 8 repetições

Quarta-feira
1. Nome do exercício - 3 séries x 12 repetições

Regras obrigatórias:
- Use somente os dias da semana em português (Segunda-feira, Terça-feira, Quarta-feira, Quinta-feira, Sexta-feira, Sábado, Domingo).
- Use exatamente o número de dias de treino informado no pedido do usuário, sempre nos dias específicos indicados.
- Cada dia de treino deve conter entre {MIN_EXERCICIOS_POR_DIA} e {MAX_EXERCICIOS_POR_DIA} exercícios, nunca menos que isso.
- Cada exercício deve estar em uma única linha, no formato "número. Nome do exercício - X séries x Y repetições".
- Utilize exclusivamente exercícios desta lista (não invente nomes, não misture idiomas, não crie variações que não estejam aqui): {EXERCICIOS_VALIDOS}
- Separe cada dia por uma linha em branco.
- Não use Markdown (sem #, *, - de lista, nem negrito).
- Não escreva introdução, explicação ou conclusão. Apenas o treino.
"""


def _montar_prompt(profile, goal, num_dias, dias_sugeridos, split_sugerido):
    return f"""
Crie um treino para o seguinte usuário.

Sexo: {profile.gender}
Idade: {profile.age}
Peso: {profile.weight} kg
Altura: {profile.height} cm
Nível de atividade: {profile.activity_level}

Objetivo:
{goal.objective}

Monte o treino usando EXATAMENTE {num_dias} dias de treino: {dias_sugeridos}.
Use uma divisão do tipo {split_sugerido}, adaptando os exercícios para o objetivo do usuário.
Cada dia deve ter entre {MIN_EXERCICIOS_POR_DIA} e {MAX_EXERCICIOS_POR_DIA} exercícios.

Siga rigorosamente o formato e as regras definidas.
"""


PADRAO_EXERCICIO = re.compile(r"^\d+\.\s*(.+?)\s*-\s*.*s[ée]rie.*$", re.IGNORECASE)


def _validar_treino(texto, num_dias_esperado):
    blocos = [b.strip() for b in texto.strip().split("\n\n") if b.strip()]

    if not blocos:
        return False

    dias_encontrados = []

    for bloco in blocos:
        linhas = [l.strip() for l in bloco.split("\n") if l.strip()]

        if not linhas:
            return False

        dia = linhas[0].lower()
        if dia not in DIAS_VALIDOS:
            return False

        if dia in dias_encontrados:
            return False
        dias_encontrados.append(dia)

        exercicios = linhas[1:]
        num_exercicios_dia = len(exercicios)

        if not (MIN_EXERCICIOS_POR_DIA <= num_exercicios_dia <= MAX_EXERCICIOS_POR_DIA):
            return False

        for linha in exercicios:
            match = PADRAO_EXERCICIO.match(linha)
            if not match:
                return False

            nome_exercicio = match.group(1).strip()
            if not nome_exercicio or len(nome_exercicio) < 3:
                return False

    return len(dias_encontrados) == num_dias_esperado


def gerar_treino(profile, goal, tentativas=3):
    num_dias = DIAS_POR_ATIVIDADE.get(profile.activity_level, 3)
    dias_sugeridos, split_sugerido = SPLITS_SUGERIDOS[num_dias]

    prompt = _montar_prompt(profile, goal, num_dias, dias_sugeridos, split_sugerido)

    ultimo_texto = None

    for tentativa in range(tentativas):
        try:
            resposta = client.chat.completions.create(
                model=os.getenv("HF_MODEL_TREINO"),
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
                max_tokens=1400,
            )

            texto = (resposta.choices[0].message.content or "").strip()
            ultimo_texto = texto

            if texto and _validar_treino(texto, num_dias):
                return texto

        except Exception as e:
            print(f"Tentativa {tentativa + 1} falhou: {e}")

    if ultimo_texto:
        raise ValueError("Não foi possível gerar um treino em formato válido após múltiplas tentativas.")
    raise ValueError("O modelo não retornou nenhuma resposta.")