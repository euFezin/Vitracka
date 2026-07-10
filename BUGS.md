# Bugs conhecidos - Vitracka 

Este arquivo documenta problemas conhecidos encontrados durante o desenvolvimento da versão **v0.4 Alpha** do Vitracka.

## Bug #003 - Desalinhamento no campo de interação da Vix AI

**Status:** Aberto

**Versão afetada:** v0.4 Alpha

**Prioridade:** Baixa

## Descrição

O campo de texto e o botão de envio da seção "Vix AI" apresentam um pequeno desalinhamento visual em determinadas situações, comprometendo o acabamento da interface.

## Impacto

Pequena inconsistência visual;
Não interfere no envio das mensagens nem no funcionamento do chat.

## Possível causa

Possível conflito entre regras de alinhamento do Flexbox, alturas dos componentes (`input` e `button`) ou estilos globais aplicados aos formulários.

## Correção planejada

* Revisar o alinhamento do formulário da Vix AI;
* Padronizar altura entre campo de texto e botão;
* Revisar estilos globais de inputs e botões;
* Validar o comportamento em diferentes resoluções.

---

## Bug #002 - Erro em função de gerar outra recomendação alimentar

**Status:** Corrigido

**Versão afetada:** v0.4 Alpha
**Versão corrigida:** v0.4.1 Alpha

**Prioridade:** Alta

### Descrição

Após alterações realizadas durante o desenvolvimento da versão v0.4 Alpha, a função de gerar nova recomendação alimentar passou a apagar a refeição existente em vez de substituí-la por uma nova.

O problema foi identificado após modificações no código e necessitou de investigação para encontrar a causa raiz.

### Impacto

Ao clicar em "gerar nova refeição", a refeição atual era removida sem que uma nova fosse gerada corretamente no lugar.

### Causa raiz

O erro estava relacionado à quantidade máxima de tokens utilizada pelo modelo de IA: o limite implementado no sistema não era suficiente para a função retornar a resposta completa ao usuário.

### Solução aplicada

* Revisado o código da função afetada;
* Substituído o modelo de IA pelo `Qwen/Qwen2.5-7B-Instruct`, que se encaixa melhor no contexto da aplicação;
* Testado para garantir que outras funcionalidades não foram afetadas.

---
---
---

## Bug #001 - Instabilidade no posicionamento da navbar

**Status:** Aberto

**Versão afetada:** v0.4 Alpha

**Prioridade:** Baixa

## Descrição

A navbar apresenta instabilidades de posicionamento em determinadas páginas do sistema.

Em algumas situações, o componente pode sobrepor partes do conteúdo principal (body) ou causar cortes no layout, prejudicando a visualização e navegação da aplicação.

## Impacto
Elementos da página podem ficar parcialmente ocultos;
Conteúdos podem ser sobrepostos pela navbar;
A experiência visual pode variar entre diferentes páginas.

## Possível causa
Possíveis conflitos relacionados ao posicionamento CSS da navbar, espaçamentos do container principal, altura do componente ou regras de layout aplicadas globalmente.

## Correção planejada
* Revisar o CSS global da navbar;
* Ajustar espaçamentos entre navbar e conteúdo principal;
* Garantir comportamento consistente em todas as páginas;
* Realizar testes de responsividade.

---
---
---

## Observações da versão

A versão **v0.4 Alpha** representa uma etapa de desenvolvimento e pode conter instabilidades.

Novos bugs encontrados durante os testes devem ser adicionados a este arquivo e corrigidos nas próximas versões.
