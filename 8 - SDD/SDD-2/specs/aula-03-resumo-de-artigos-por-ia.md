# Spec — Aula 3: Resumo de artigos por IA

> Parte de **Specs do Projeto 2 — Agregador de Notícias com resumo por IA** — spec 3 de 6. As specs são cumulativas: esta assume o estado deixado pela anterior.

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

**Objetivo (por quê):** gerar um resumo curto de cada artigo usando IA, o valor central do produto.

**Contexto:** app com fontes e artigos (Aulas 1–2). Ainda não há nenhuma chamada de IA.

**Requisitos funcionais:**
1. Gerar, sob demanda, um resumo em português de um artigo, a partir do seu `titulo` + `conteudo`, chamando a API do Claude.
2. **Cachear** o resumo: uma vez gerado, é persistido e reutilizado nas próximas chamadas (não chama a API de novo).
3. Tratar falha da API (timeout/erro) sem derrubar a requisição — retornar erro claro e não gravar resumo inválido.

**Alteração em `artigo`:** adicionar `resumo` (texto, nulo até ser gerado).

**Contrato de API:**
- `GET /artigos/:id/resumo` — se já houver resumo, retorna o cacheado; senão, gera via IA, salva e retorna. 404 se o artigo não existir; 502 (ou similar) com `{ "erro": ... }` se a IA falhar.

**Critérios de aceite:**
- Primeira chamada a `GET /artigos/:id/resumo` gera o resumo e o persiste; a segunda retorna o mesmo resumo **sem** nova chamada à API.
- Artigo inexistente retorna 404.
- Falha simulada da API é tratada: a requisição não quebra e nenhum resumo inválido é salvo.

**Fora de escopo:** categorização, digest, filtros.

**Restrições técnicas:** usar o SDK `@anthropic-ai/sdk` (Messages API); chave por `ANTHROPIC_API_KEY`; escolher um modelo econômico (ex.: Claude Haiku) e registrar no `CLAUDE.md`; prompt de resumo curto e objetivo; limitar tamanho do conteúdo enviado para controlar custo/latência.
