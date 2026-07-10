# Vitracka

Vitracka é uma aplicação fitness inteligente que utiliza Inteligência Artificial para auxiliar usuários no planejamento nutricional e de treinamento, oferecendo cálculo metabólico, geração de refeições personalizadas, criação de treinos e suporte para objetivos como bulking, cutting e manutenção.

⚠️ Projeto em desenvolvimento.
Atualmente em fase de MVP e recebendo melhorias contínuas.

## Roadmap

- [x] Sistema de cálculo de TMB/TDEE
- [x] Definição de objetivos (bulk/cut/manutenção)
- [x] Geração de refeições
- [x] Integração inicial com IA local via LM Studio
- [x] Migração da camada de IA para modelos da Hugging Face
- [x] Chat nutricional
- [x] Persistência com banco de dados
- [x] Histórico de progresso
- [x] Login e autenticação
- [x] Implementação de Política e Privacidade
- [x] Página de configurações de conta
- [ ] Implementação de um Mascote para o aplicativo
- [ ] Dashboard de métricas
- [ ] Exportar plano (dieta + treino) em PDF
- [ ] Upload de fotos para análise corporal

## Status atual

O sistema já realiza:

- Cálculo metabólico individualizado.
- Recomendação de ingestão calórica conforme objetivo do usuário.
- Distribuição personalizada de macronutrientes.
- Geração de refeições baseada em metas nutricionais.
- Chat contextual com Inteligência Artificial através da Vix AI.
- Assistência da IA em dúvidas relacionadas à nutrição, musculação e treinamento.
- Geração de planos de treino personalizados utilizando Inteligência Artificial.
- Gerenciamento de conta, incluindo alteração de dados pessoais, senha e exclusão de usuário.
- Sistema de autenticação e controle de acesso de usuários.
- Dashboard personalizado para acompanhamento das informações do usuário.


## Tecnologias

### Backend
- Python
- Flask
- SQLAlchemy
- Flask-Migrate
- Alembic

### Frontend
- HTML
- CSS
- JavaScript
- Jinja2

### Banco de dados
- MySQL

### Inteligência Artificial
- Hugging Face Transformers
- Modelos LLM locais

## Banco de dados local

Crie o banco no MySQL:

```sql
CREATE DATABASE vitracka CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

No PowerShell, informe sua senha do MySQL antes de criar as tabelas:

```powershell
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="sua_senha_do_mysql"
$env:MYSQL_DATABASE="vitracka"

.\venv\Scripts\python.exe -m flask --app app db upgrade
.\venv\Scripts\python.exe app.py
```

O projeto usa SQLAlchemy com PyMySQL e Flask-Migrate. O schema SQL completo tambem esta em `database/schema.sql`.

Para gerar uma nova migration depois de alterar modelos:

```powershell
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="sua_senha_do_mysql"
$env:MYSQL_DATABASE="vitracka"

.\venv\Scripts\python.exe -m flask --app app db migrate -m "descricao da mudanca"
.\venv\Scripts\python.exe -m flask --app app db upgrade
```

O sistema cria as tabelas de usuarios, perfis fisicos, objetivos, planos, refeicoes geradas e check-ins de progresso.

## Desenvolvimento assistido por IA

A Inteligência Artificial foi utilizada como ferramenta de apoio durante o desenvolvimento, principalmente para:

- Pesquisa e validação de abordagens técnicas.
- Auxílio na estruturação inicial de componentes e banco de dados.
- Revisão de código e resolução de problemas.

A arquitetura, regras de negócio e evolução do sistema foram desenvolvidas e validadas durante o processo de aprendizado.