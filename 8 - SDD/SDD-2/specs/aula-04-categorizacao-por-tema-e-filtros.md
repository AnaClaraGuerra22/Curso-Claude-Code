# Spec — Aula 4: Categorização por tema e filtros

> Parte de **Specs do Projeto 2 — Agregador de Notícias com resumo por IA** — spec 4 de 6. As specs são cumulativas: esta assume o estado deixado pela anterior.

---

## Contexto do projeto

**Stack:** Node.js 20+ · Express · SQLite (better-sqlite3) · rss-parser · SDK do Claude para JS (`@anthropic-ai/sdk`)
**Uso:** cada spec corresponde a uma aula. É o insumo que o aluno dá ao Claude Code para gerar o plano e implementar o incremento. As specs são cumulativas — cada uma assume o estado deixado pela anterior.

**Convenções gerais do projeto (valem para todas as specs):**
- API REST em Express; respostas em JSON; datas no formato ISO `YYYY-MM-DD`.
- Persistência em SQLite num arquivo local; a estrutura do banco é criada na inicialização se não existir.
- Erros de validação retornam HTTP 422 com corpo `{ "erro": "<mensagem clara>" }`; recurso inexistente retorna 404.
- A chave da API do Claude vem de variável de ambiente (`ANTHROPIC_API_KEY`) — nunca hardcoded.
- Código organizado em módulos (rotas, serviços, acesso a dados) e versionado no Git a cada aula.

---

**Objetivo (por quê):** organizar os artigos por tema e permitir encontrar o que interessa.

**Contexto:** artigos com resumo por IA (Aulas 1–3). Ainda sem categorização nem filtros.

**Requisitos funcionais:**
1. Classificar cada artigo por **tema** (ex.: tecnologia, economia, esportes) — via IA ou por palavras-chave (decidir e registrar no `CLAUDE.md`).
2. Filtrar artigos combinando: `tema`, `fonte` e período (`data_inicio`, `data_fim`). Todos opcionais e combináveis.

**Alteração em `artigo`:** adicionar `tema` (texto, pode ser nulo até classificar).

**Contrato de API:**
- `POST /classificar` — classifica os artigos ainda sem tema; retorna `{ classificados: <n> }`.
- `GET /artigos` passa a aceitar os parâmetros opcionais `tema`, `fonte`, `data_inicio`, `data_fim`, combinados por E lógico.

**Critérios de aceite:**
- Após `POST /classificar`, os artigos têm `tema` preenchido.
- `GET /artigos?tema=tecnologia&fonte=<x>` combina os filtros corretamente.
- Período por `data_inicio`/`data_fim` funciona isolado e junto dos demais filtros.
- Parâmetros inválidos (ex.: período invertido) retornam 422.

**Fora de escopo:** digest, favoritos, dashboard.

**Restrições técnicas:** montar a query de filtros dinamicamente com parâmetros vinculados (sem concatenar SQL); se a classificação for por IA, reaproveitar o cliente e o cuidado de custo da Aula 3.
