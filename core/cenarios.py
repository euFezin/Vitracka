def gerar_cenarios(tdee, peso, objetivo):
    
    cenarios = []
    
    if objetivo == 'bulking':
        
        cenarios.append({
            "nome": 'Lean Bulk',
            "calorias": tdee * 1.08,
            "descricao": 'Ganho de massa controlado com mínimo de gordura.',
            "fator_proteina": 2.2,
            "fator_gordura": 0.8
        })
        
        cenarios.append({
            "nome": 'Bulking Clássico',
            "calorias": tdee * 1.15,
            "descricao": 'Equilíbrio entre ganho muscular e aumento de gordura',
            "fator_proteina": 2.2,
            "fator_gordura": 1
        })
        
        cenarios.append({
            "nome": 'Bulking Agressivo',
            "calorias": tdee * 1.25,
            "descricao": 'Ganho rápido de peso com maior acúmulo de gordura.',
            "fator_proteina": 2.3,
            "fator_gordura": 1.1
        })
        
    elif objetivo == 'cutting':
        
        cenarios.append({
            "nome": 'Cutting Controlado',
            "calorias": tdee * 0.90,
            "descricao": 'Perda de gordura lenta e sustentável, mantendo massa muscular.',
            "fator_proteina": 2.2,
            "fator_gordura": 0.7
        })
        
        cenarios.append({
            "nome": 'Cutting Agressivo',
            "calorias": tdee * 0.75,
            "descricao": 'Perda rápida de gordura com maior risco de perda de massa.',
            "fator_proteina": 2.2,
            "fator_gordura": 0.5
        })
    
    else: 
        
        cenarios.append({
            "nome": 'Manutenção',
            "calorias": tdee,
            "descricao": 'Manter o peso atual com equilíbrio energético.',
            "fator_proteina": 2,
            "fator_gordura": 1
        })
    
    return cenarios