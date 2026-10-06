# Spec — Aula 5: Digest diário e testes automatizados

> Parte de **Specs do Projeto 2 — Agregador de Notícias com resumo por IA** — spec 5 de 6. As specs são cumulativas: esta assume o estado deixado pela anterior.

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

**Objetivo (por quê):** entregar um resumo consolidado do dia e blindar o comportamento com testes.

**Contexto:** app com artigos, resumos e categorização (Aulas 1–4). Ainda sem digest nem testes.

**Requisitos funcionais:**
1. Gerar um **digest diário**: os artigos de uma data (opcionalmente de um tema), cada um com seu resumo, numa saída única.
2. Cobrir os fluxos principais com **testes automatizados** (importar, listar, filtrar, resumo, digest, casos de erro), com a chamada de IA **mockada**.

**Contrato de API:**
- `GET /digest?data=YYYY-MM-DD` — retorna `{ data, artigos: [{ titulo, fonte, tema, resumo, link }] }` do dia; aceita `&tema=` opcional.

**Critérios de aceite:**
- `GET /digest?data=2026-08-19` retorna os artigos daquele dia com seus resumos.
- Filtrar o digest por tema funciona.
- Dia sem artigos retorna lista vazia, sem erro.
- A suíte de testes (Vitest) cobre os fluxos principais, com a IA mockada, e passa integralmente **sem** chamar a API real.

**Fora de escopo:** favoritos, dashboard, deploy.

**Restrições técnicas:** testes com Vitest e supertest (ou o cliente HTTP do runner) sobre um banco de teste isolado; mock do SDK do Claude para não gastar tokens nos testes.
