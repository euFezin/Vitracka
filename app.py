from flask import Flask, render_template, request, redirect, url_for, session
from core.cenarios import gerar_cenarios
from core.ia_explicacao import gerar_explicacao
from core.chat import gerar_resposta_chat
from core.refeicoes import gerar_refeicao, gerar_todas_refeicoes

app = Flask(__name__)
app.secret_key = "musculacao_Vitracka"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/objetivo')
def objetivo():
    return render_template('objetivo.html')

@app.route('/salvar-objetivo', methods=['POST'])
def salvar_objetivo():
    session['objetivo'] = request.form['objetivo']
    return redirect(url_for('dados'))

@app.route('/dados', methods=['GET', 'POST'])
def dados():
    objetivo = session.get('objetivo')
    
    if request.method == 'POST':
        session['genero'] = request.form['genero']
        session['peso'] = float(request.form['peso'])
        session['altura'] = float(request.form['altura'])
        session['idade'] = int(request.form['idade'])
        
        return redirect(url_for('atividade'))
    
    return render_template('dados.html', objetivo=objetivo)

@app.route('/atividade', methods=['GET', 'POST'])
def atividade():
    if request.method == 'POST':
        session['atividade'] = request.form['atividade']
        return redirect(url_for('calcular'))
    
    return render_template('atividade.html')

@app.route('/calcular')
def calcular():
    
    genero = session.get('genero')
    peso = session.get('peso')
    altura = session.get('altura')
    idade = session.get('idade')
    objetivo = session.get('objetivo')
    atividade = session.get('atividade')
    
    #Aqui será feito o cálculo de Taxa Metabólica Basal (TMB)
    if genero == "masculino":
        tmb = 10 * peso + 6.25 * altura - 5 * idade + 5
    else:
        tmb = 10 * peso + 6.25 * altura - 5 * idade - 161
        
    fatores = {
        "sedentario": 1.2,
        "leve": 1.375,
        "moderado": 1.55,
        "intenso": 1.725
    }
    
    # TDEE é a quantidade total de calorias gastas no dia, levando em conta os fatores do seu dia a dia
    tdee = tmb * fatores.get(atividade, 1.2)
    
    # Aqui o cálculo será ajustado de acordo com o objetivo
    if objetivo == 'bulking':
        calorias = tdee * 1.15
    elif objetivo == 'cutting':
        calorias = tdee * 0.80
    else: 
        calorias = tdee
        
    cenarios = gerar_cenarios(tdee, peso, objetivo)
    
    for cenario in cenarios:
        calorias = cenario['calorias']
        
        proteina = peso * cenario['fator_proteina']
        gordura = peso * cenario['fator_gordura']
        carboidratos = (calorias - (proteina*4 + gordura*9)) / 4
        
        cenario['proteina'] = round(proteina)
        cenario['gordura'] = round(gordura)
        cenario['carboidratos'] = round(carboidratos)
        cenario['calorias'] = round(calorias)
    
    return render_template(
        'resultado.html',
        cenarios=cenarios
    )
    
@app.route('/selecionar-plano', methods=['POST'])
def selecionar_plano():
    session['plano_nome'] = request.form['nome']
    session['plano_calorias'] = request.form['calorias']
    session['plano_proteina'] = request.form['proteina']
    session['plano_carboidratos'] = request.form['carboidratos']
    session['plano_gordura'] = request.form['gordura']
    
    return redirect(url_for('explicacao'))

@app.route('/explicacao')
def explicacao():

    plano = {
        "nome": session.get('plano_nome'),
        "calorias": session.get('plano_calorias'),
        "proteina": session.get('plano_proteina'),
        "carboidratos": session.get('plano_carboidratos'),
        "gordura": session.get('plano_gordura')
    }
    
    texto_ia = gerar_explicacao(
        plano=plano["nome"],
        objetivo=session.get("objetivo"),
        peso=session.get("peso"),
        atividade=session.get("atividade")
    )

    return render_template(
        'explicacao.html', 
        plano= plano,
        texto_ia= texto_ia
        )
    
@app.route('/refeicoes')
def refeicoes():
    plano = {
        "nome": session.get('plano_nome'),
        "calorias": session.get('plano_calorias'),
        "proteina": session.get('plano_proteina'),
        "carboidratos": session.get('plano_carboidratos'),
        "gordura": session.get('plano_gordura')
    }
    
    if 'refeicoes' not in session:
        session['refeicoes'] = gerar_todas_refeicoes(plano)
        session.modified = True
        
    return render_template(
        'refeicoes.html',
        plano = plano,
        refeicoes = session['refeicoes'] 
    )
    
@app.route('/regenerar-refeicao', methods = ['POST'])
def regenerar_refeicao():
    refeicao = request.form['refeicao']
    
    plano = {
        "nome": session.get('plano_nome'),
        "calorias": session.get('plano_calorias'),
        "proteina": session.get('plano_proteina'),
        "carboidratos": session.get('plano_carboidratos'),
        "gordura": session.get('plano_gordura')
    }
    
    refeicoes = session.get('refeicoes', {})
    refeicoes[refeicao] = gerar_refeicao(refeicao, plano)
    session['refeicoes'] = refeicoes
    session.modified = True
    
    return redirect(url_for('refeicoes'))
    
@app.route('/chat', methods=['GET', 'POST'])
def chat():
 
    if 'historico_chat' not in session:
        session['historico_chat'] = []
 
    if request.method == 'POST':
        pergunta = request.form['pergunta']
 
        historico = session['historico_chat']
        historico.append({"role": "user", "content": pergunta})
 
        resposta = gerar_resposta_chat(historico)
 
        historico.append({"role": "assistant", "content": resposta})
        session['historico_chat'] = historico
        session.modified = True
 
    return render_template('chat.html', historico=session.get('historico_chat', []))
 
 
@app.route('/limpar-chat', methods=['POST'])
def limpar_chat():
    session.pop('historico_chat', None)
    return redirect(url_for('chat'))

if __name__ == '__main__':
    app.run(debug=True)