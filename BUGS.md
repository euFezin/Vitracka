# Bugs conhecidos - Vitracka v0.4 Alpha

Este arquivo documenta problemas conhecidos encontrados durante o desenvolvimento da versão **v0.4 Alpha** do Vitracka.

---

## Bug #001 - Erro em função de gerar outra recomendação alimentar

**Status:** Aberto

**Versão afetada:** v0.4 Alpha

**Prioridade:** Alta

### Descrição

Após alterações realizadas durante o desenvolvimento da versão v0.4 Alpha, a determinada função do sistema passou a apresentar comportamento incorreto.

O problema foi identificado após modificações no código e ainda necessita de investigação para encontrar a causa raiz.

### Impacto

A funcionalidade relacionada à função afetada não funcionará corretamente, afetando diretamente a experiência do usuário.

### Possível causa

Uma possível causa para esse erro está relacionada a substituição da IA Local utilizada em versões passadas pela implementação de uma IA através do Hugging Face

### Correção planejada

* Revisar o código da função afetada;
* Identificar a origem do erro;
* Aplicar a correção;
* Realizar testes para garantir que outras funcionalidades não sejam afetadas.

---
---
---

## Bug #002 - Instabilidade no posicionamento da navbar

**Status:** Aberto

**Versão afetada:** v0.4 Alpha

**Prioridade:** Média

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
