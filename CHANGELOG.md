# Changelog — Vitracka (Web)

Histórico de alterações e melhorias realizadas no projeto.

## [0.6.0-alpha] - 2026-07-13

### Adicionado
- **Tracker de água e sono no Dashboard**: cards antes marcados como "Em breve" agora funcionam de verdade — água com botões de incremento rápido (+250ml/+500ml) e botão de reset, sono com campo de horas registrado ao sair do campo.
- **Página de Métricas** (`/metricas`): nova tela com médias diária, semanal e mensal de água e sono, além de histórico dos últimos 30 dias em formato de timeline. Acessível por um link no card de progresso do Dashboard.
- Novos endpoints web (`/tracker/agua`, `/tracker/sono`) autenticados por sessão, consumidos via JavaScript sem recarregar a página.

### Melhorado
- **Geração de treino reformulada**: o número de dias de treino por semana agora é calculado pelo backend com base no nível de atividade do usuário (3 a 6 dias), em vez de deixar a IA escolher livremente — corrigindo a tendência do modelo de sempre gerar o mesmo padrão "Segunda/Quarta/Sexta".
- Prompt de geração de treino reescrito com uma lista fechada de exercícios válidos, evitando nomes inventados ou sem sentido.
- Adicionada validação automática do treino gerado (formato, quantidade de exercícios por dia, nomes válidos) com nova tentativa automática em caso de resposta malformada, antes de salvar no banco.
- Formato de cada exercício simplificado para uma única linha (nome e séries/repetições juntos), mais legível que o formato anterior em duas linhas.
- Lógica de busca/criação do registro diário de água e sono centralizada em `core/services.py`, reaproveitada tanto pela API mobile quanto pelas rotas web.

### Corrigido
- Nenhuma correção relevante nesta versão.

### Notas para a próxima versão
- Passos (contagem) seguem propositalmente fora de uso — coluna já existe no banco, aguardando decisão sobre sincronização automática via sensor do celular.
- Meta de água ainda não é configurável pelo usuário (fixa em 3000ml).

<br>

## [0.5.3-alpha] - 2026-07-12

**Status:** Publicada

### Adicionado

* Novo model `DailyTracker`, permitindo o registro diário de consumo de água e horas de sono por usuário, com estrutura já preparada para inclusão futura de contagem de passos.
* Novos endpoints de API para o tracker diário: consulta do registro do dia atual, atualização de água, atualização de sono e histórico com cálculo de médias (diária, semanal e mensal).
* Migration de banco de dados para a nova tabela `daily_trackers`, com restrição de unicidade por usuário e data.

### Melhorado

* Cálculo de médias de consumo de água e sono realizado diretamente no backend, evitando processamento adicional no lado do cliente.
* Consulta do tracker diário já retorna (ou cria automaticamente) o registro do dia corrente, simplificando o consumo por aplicações clientes.

### Corrigido

* Nenhuma correção relevante nesta versão.

<br>

## [0.5.2-alpha] - 2026-07-11

**Status:** Publicada

### Adicionado

* Criação de rotas de API para disponibilização dos recursos do Vitracka, permitindo a comunicação entre o backend e futuras aplicações clientes.
* Implementação da estrutura inicial de endpoints preparados para integração com o aplicativo mobile.
* Preparação da arquitetura da aplicação para suportar múltiplas interfaces de acesso, mantendo o backend independente do frontend.

### Melhorado

* Evolução da organização das rotas da aplicação, separando funcionalidades web e APIs de forma mais clara.
* Ajustes na estrutura do backend visando maior escalabilidade e facilitando a expansão do Vitracka para novas plataformas.
* Melhor preparação da camada de dados e serviços para consumo externo através de requisições HTTP.

### Corrigido

* Ajustes internos na organização dos módulos de rotas.
* Correções estruturais relacionadas à separação de responsabilidades entre páginas web e serviços da API.

<br>

## [0.5.1-alpha] - 2026-07-10

**Status:** Publicada

### Adicionado
- Implementação do histórico de conversas da IA Vix, permitindo acessar, continuar e gerenciar chats anteriores.

### Melhorado
- Reformulação completa da interface da IA Vix, proporcionando uma experiência de conversa mais moderna, organizada e intuitiva.
- Redesign da página de chat com a adição de uma barra lateral para gerenciamento das conversas.
- Refatoração da estrutura da aplicação com a modularização das rotas, tornando o código mais organizado, escalável e de fácil manutenção.
- Refatoração do arquivo principal da aplicação (`app.py`), reduzindo sua complexidade e preparando a base para futuras funcionalidades.
- Ajustes gerais na arquitetura do projeto visando facilitar a evolução e manutenção do Vitracka.

### Corrigido
- Correções de layout e alinhamento na interface do chat.
- Ajustes na organização dos componentes da página de conversas.
- Correções internas relacionadas à navegação e estrutura das rotas.

<br>

## [0.5.0-alpha] - 2026-07-09

**Status:** Publicada

### Adicionado
- Implementação do sistema de geração de treinos personalizados utilizando Inteligência Artificial.
- Criação da página de configurações do usuário, permitindo a alteração de nome, e-mail, senha, dados físicos e exclusão da conta.
- Expansão das capacidades da IA Vix para auxiliar em dúvidas relacionadas a musculação, exercícios e treinamento.

### Melhorado
- Aprimoramento da interface geral do dashboard do usuário.
- Melhorias na experiência de interação com a IA, incluindo recomendações mais abrangentes relacionadas a treino e performance.

---

### Observações

Versão focada na expansão das funcionalidades principais do Vitracka, introduzindo recursos relacionados à geração de treinos por Inteligência Artificial e personalização da conta do usuário.

Por se tratar de uma versão Alpha, podem existir instabilidades e comportamentos inesperados que serão tratados em versões futuras.

<br>

## [0.4.1-alpha] - 2026-07-08

**Status:** Publicada

### Corrigido
- Bug no botão "gerar nova refeição": ao clicar, a refeição existente era apagada em vez de ser substituída pela nova gerada.

---

### Observações

Versão de manutenção focada em correção de bugs reportados na geração de refeições pela IA.

Por se tratar de uma versão Alpha, podem existir instabilidades e comportamentos inesperados que serão tratados em versões futuras.