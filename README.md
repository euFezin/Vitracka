# Vitracka

Vitracka é uma aplicação fitness com suporte de IA voltada para cálculo nutricional, geração de refeições personalizadas e assistência inteligente para objetivos de bulking, cutting e manutenção.

⚠️ Projeto em desenvolvimento.
Atualmente em fase de MVP e recebendo melhorias contínuas.

## Roadmap

- [x] Sistema de cálculo de TMB/TDEE
- [x] Definição de objetivos (bulk/cut/manutenção)
- [x] Geração de refeições
- [x] Integração com IA local (LM Studio)
- [x] Chat nutricional
- [x] Persistência com banco de dados
- [x] Histórico de progresso
- [x] Login e autenticação
- [ ] Dashboard de métricas
- [ ] Upload de fotos para análise corporal

## Status atual

O sistema já realiza:
- cálculo metabólico
- recomendação calórica
- distribuição de macronutrientes
- geração de refeições baseada em metas
- chat contextual com IA local
- login e autenticação de usuário


## Tecnologias

Python  
Flask  
HTML  
CSS  
LM Studio  
Gemma 3  
Jinja2
MySQL
Alembic

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

- A estrutura inicial do banco de dados foi gerada com auxílio de IA generativa (ChatGPT Codex) e integrada ao projeto após validação e ajustes.
- Parte da estrutura inicial e estilização do projeto também foi acelerada com auxílio de IA.
- A arquitetura, lógica de negócio e evolução do sistema foram desenvolvidas durante o processo de aprendizado.
