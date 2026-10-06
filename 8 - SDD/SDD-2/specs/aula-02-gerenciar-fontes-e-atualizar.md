# Spec — Aula 2: Gerenciar fontes e atualizar

> Parte de **Specs do Projeto 2 — Agregador de Notícias com resumo por IA** — spec 2 de 6. As specs são cumulativas: esta assume o estado deixado pela anterior.

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

**Objetivo (por quê):** permitir cadastrar várias fontes de notícias e atualizar todas de uma vez, com validação.

**Contexto:** já existe importação de um feed e listagem de artigos (Aula 1). Esta spec introduz o conceito de **fonte** persistente e a atualização em lote.

**Requisitos funcionais:**
1. Gerenciar fontes: adicionar, listar e remover feeds cadastrados.
2. Validar ao adicionar: URL bem formada e que responde como RSS válido; URL duplicada é rejeitada.
3. Atualizar: buscar artigos novos de **todas** as fontes cadastradas de uma vez.

**Modelo de dados — `fonte`:**
- `id` (inteiro, automático)
- `nome` (texto — pode vir do título do feed)
- `url` (texto, único)

**Alteração em `artigo`:** associar `fonte_id` ao artigo importado.

**Contrato de API:**
- `POST /fontes` — recebe `{ url }`; valida, resolve o nome pelo feed e salva; retorna 201 com a fonte.
- `GET /fontes` — lista as fontes.
- `DELETE /fontes/:id` — remove a fonte; 404 se não existir.
- `POST /atualizar` — percorre todas as fontes, importa artigos novos e retorna `{ importados: <n> }`.

**Critérios de aceite:**
- `POST /fontes` com URL válida cria a fonte; URL inválida ou que não é RSS retorna 422 com mensagem clara; URL duplicada retorna 422.
- `DELETE /fontes/:id` remove; id inexistente retorna 404.
- `POST /atualizar` traz apenas artigos novos de todas as fontes, sem duplicar.

**Fora de escopo:** resumo por IA, categorias, filtros.

**Restrições técnicas:** validar o feed tentando parseá-lo antes de salvar; tratar fonte fora do ar sem derrubar a atualização das demais.
