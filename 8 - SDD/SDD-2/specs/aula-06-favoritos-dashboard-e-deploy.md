# Spec — Aula 6: Favoritos, dashboard e deploy

> Parte de **Specs do Projeto 2 — Agregador de Notícias com resumo por IA** — spec 6 de 6. As specs são cumulativas: esta assume o estado deixado pela anterior.

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

**Objetivo (por quê):** dar ao usuário uma interface para ler e guardar notícias, e publicar o app.

**Contexto:** app completo e testado (Aulas 1–5). Falta favoritar, visualizar e publicar.

**Requisitos funcionais:**
1. Favoritar e desfavoritar artigos; listar favoritos.
2. Servir um **mini-dashboard HTML** que mostra o digest do dia, os resumos (sob demanda) e os favoritos.
3. Preparar o app para **deploy**: porta e `ANTHROPIC_API_KEY` por variável de ambiente.

**Alteração em `artigo`:** adicionar `favorito` (booleano, padrão falso).

**Contrato de API:**
- `POST /artigos/:id/favoritar` e `DELETE /artigos/:id/favoritar` — marca/desmarca; 404 se não existir.
- `GET /favoritos` — lista os artigos favoritados.
- `GET /` (ou `/dashboard`) — serve a página HTML do dashboard.

**Critérios de aceite:**
- Favoritar/desfavoritar reflete em `GET /favoritos`.
- O dashboard exibe o digest do dia, permite abrir o resumo de um artigo e mostra os favoritos, consumindo os endpoints existentes.
- O app roda fora da máquina local (deploy), com porta e chave da API vindas de variáveis de ambiente.

**Fora de escopo:** autenticação, multiusuário, banco externo (extensões avançadas).

**Restrições técnicas:** dashboard como HTML simples servido pelo Express, com JS de front leve (fetch nos endpoints; gráfico opcional via Chart.js por CDN); nenhuma credencial hardcoded.
