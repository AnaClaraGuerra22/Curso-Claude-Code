# Spec — Aula 1: Ler um feed RSS e listar artigos

> Parte de **Specs do Projeto 2 — Agregador de Notícias com resumo por IA** — spec 1 de 6. As specs são cumulativas: esta assume o estado deixado pela anterior.

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

**Objetivo (por quê):** trazer notícias de uma fonte RSS para dentro do app e listá-las, estabelecendo a base persistente.

**Contexto:** projeto novo, ainda sem nada implementado. Primeira feature.

**Requisitos funcionais:**
1. Dada a URL de um feed RSS, buscar os artigos e guardá-los no banco, com: `titulo`, `link`, `data_publicacao`, `fonte` (origem do feed) e `conteudo` (resumo/descrição do item RSS, quando houver).
2. Listar os artigos guardados, mais recentes primeiro.
3. Reprocessar o mesmo feed **não** deve duplicar artigos já existentes (deduplicar por `link`).

**Modelo de dados — `artigo`:**
- `id` (inteiro, automático)
- `titulo` (texto)
- `link` (texto, único)
- `data_publicacao` (texto ISO)
- `fonte` (texto)
- `conteudo` (texto, pode ser vazio)

**Contrato de API:**
- `POST /feeds/importar` — recebe `{ url }`; busca o feed via rss-parser, salva os artigos novos e retorna `{ importados: <n> }`.
- `GET /artigos` — retorna a lista de artigos ordenada por `data_publicacao` decrescente.

**Critérios de aceite:**
- Importar um feed válido salva os artigos e `GET /artigos` os lista, mais recentes primeiro.
- Importar o mesmo feed de novo não duplica artigos (`importados` reflete só os novos).
- Os artigos persistem após reiniciar o servidor.

**Fora de escopo:** gerenciar múltiplas fontes, resumo por IA, categorias, filtros, autenticação.

**Restrições técnicas:** usar rss-parser para ler o feed; SQLite via better-sqlite3; deduplicação por `link` (índice único).
