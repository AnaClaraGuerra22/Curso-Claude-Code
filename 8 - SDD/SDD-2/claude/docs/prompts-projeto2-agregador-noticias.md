# Roteiro de Prompts — Projeto 2 (Agregador de Notícias, JavaScript)

Prompts sugeridos para o Claude Code, aula a aula, seguindo o fluxo completo de SDD:

> **Plano → (revisar) → Escopo → Implementação → Verificação → Commit**

Copie e cole, ajustando os caminhos dos arquivos de spec ao seu repositório. Os prompts são propositalmente **magros**: o peso mora nas specs e no `CLAUDE.md`. Se precisar explicar muita coisa no chat, atualize a spec.

---

## Atalho reutilizável (opcional, mas recomendado)

Crie um slash command para não digitar o ritual toda aula. No projeto: `.claude/commands/implementar-spec.md` com o conteúdo:

```
Leia a spec em: $ARGUMENTS

1. Entre em plan mode e me proponha o plano de implementação. NÃO altere arquivos ainda.
2. Aguarde minha aprovação.
3. Implemente APENAS o que está nesta spec — não adiante features de aulas futuras.
4. Respeite as convenções e decisões registradas no CLAUDE.md.
5. Ao final, verifique o resultado contra os "Critérios de aceite" da spec e me diga, item a item, se cada um passou.
```

Uso em aula: `/implementar-spec specs/aula-3-resumo-ia.md`

---

## Aula 1 — Setup + CLAUDE.md + primeira spec

**Passo 1 — Criar o esqueleto e o CLAUDE.md (antes de qualquer feature):**
```
Vamos iniciar um projeto de API "Agregador de Notícias com resumo por IA".
Stack: Node.js 20+, Express, SQLite (better-sqlite3), rss-parser e o SDK do Claude
para JS (@anthropic-ai/sdk).

Antes de implementar qualquer coisa, crie o esqueleto do projeto e um arquivo CLAUDE.md
com: descrição do projeto, stack, como rodar, estrutura de pastas, e estas convenções —
datas em ISO YYYY-MM-DD; erros de validação em HTTP 422 no formato { "erro": "<mensagem>" };
recurso inexistente em 404; a chave da API SEMPRE via variável de ambiente ANTHROPIC_API_KEY,
nunca hardcoded; banco SQLite em arquivo local criado na inicialização.
Entre em plan mode primeiro e me mostre o plano antes de criar os arquivos.
```

**Passo 2 — Implementar a primeira spec:**
```
/implementar-spec specs/aula-1-feed-artigos.md
```
(ou o equivalente sem slash command: "Leia a spec em specs/aula-1-feed-artigos.md, entre em plan mode, mostre o plano, implemente só esta spec respeitando o CLAUDE.md e verifique os critérios de aceite.")

**Passo 3 — Fechar a aula:**
```
Suba o servidor e me mostre como testar POST /feeds/importar (com uma URL de feed
real) e GET /artigos. Confirme que reimportar não duplica. Depois faça o commit inicial.
```

---

## Aula 2 — Gerenciar fontes e atualizar

**Plano + implementação:**
```
/implementar-spec specs/aula-2-fontes-atualizar.md
```

**Reforço em plan mode (casos de erro):**
```
No plano, garanta que POST /fontes valide a URL parseando o feed antes de salvar
(URL inválida ou não-RSS → 422; duplicada → 422), e que POST /atualizar continue
funcionando mesmo se uma das fontes estiver fora do ar. Ajuste antes de implementar.
```

**Verificação + memória + commit:**
```
Teste cada critério de aceite (fonte válida, inválida, duplicada, DELETE inexistente,
atualizar sem duplicar). Registre no CLAUDE.md decisões novas (ex.: como o nome da fonte
é resolvido). Faça o commit.
```

---

## Aula 3 — Resumo por IA (introduz a chamada externa)

**Decisão + cuidado antes de codar:**
```
Antes de implementar, revise comigo a estratégia da chamada de IA (Claude): resumo sob
demanda, escolha de um modelo econômico (ex.: Claude Haiku), cache do resultado no próprio
artigo, tratamento de falha (sem gravar resumo inválido) e limite de tamanho do conteúdo
enviado para controlar custo. Registre essas decisões no CLAUDE.md.
```

**Plano + implementação:**
```
/implementar-spec specs/aula-3-resumo-ia.md
```

**Verificação + commit:**
```
Verifique: primeira chamada gera e persiste o resumo; segunda chamada NÃO chama a API
de novo (usa cache); artigo inexistente → 404; falha simulada da API é tratada.
Confirme que a chave vem de ANTHROPIC_API_KEY. Atualize o CLAUDE.md e faça o commit.
```

---

## Aula 4 — Categorização por tema e filtros

**Decisão de spec (bom momento didático):**
```
Antes de implementar, me ajude a decidir e registrar no CLAUDE.md: a classificação por
tema será via IA ou por palavras-chave? Recomende uma opção considerando custo e
previsibilidade, e explique o porquê.
```

**Plano + implementação:**
```
/implementar-spec specs/aula-4-categorias-filtros.md
```

**Verificação + commit:**
```
Teste POST /classificar e os filtros combinados de GET /artigos (tema + fonte + período),
cada um isolado e todos juntos, além de período invertido (deve dar 422). Confirme que a
query usa parâmetros vinculados, não concatenação de SQL. Atualize o CLAUDE.md e commite.
```

---

## Aula 5 — Digest diário e testes automatizados

**Plano + implementação:**
```
/implementar-spec specs/aula-5-digest-testes.md
```

**Verificação com subagente (novidade da aula):**
```
Rode a suíte de testes (Vitest) e me mostre o resultado — confirme que a IA está mockada
e que nenhum teste chama a API real. Em seguida, use um subagente para revisar o código
desta feature contra a spec e apontar casos não cobertos ou erros de correção. Itere no
que ele encontrar.
```

**Commit:**
```
Com os testes passando, registre no CLAUDE.md o comando de testes e a estratégia de mock,
e faça o commit.
```

---

## Aula 6 — Favoritos, dashboard e deploy

**Plano + implementação:**
```
/implementar-spec specs/aula-6-favoritos-dashboard-deploy.md
```

**Cuidados no plano:**
```
No plano, garanta: dashboard como HTML simples servido pelo Express, consumindo os
endpoints existentes via fetch (gráfico opcional via Chart.js por CDN); porta e
ANTHROPIC_API_KEY vindas de variáveis de ambiente; nenhuma credencial hardcoded.
```

**Verificação + entrega:**
```
Teste favoritar/desfavoritar e GET /favoritos; abra o dashboard e confira o digest do dia,
a abertura de resumo e a lista de favoritos. Depois me guie no deploy usando variáveis de
ambiente. Atualize o CLAUDE.md com as instruções de deploy e faça o commit final.
```

---

## Lembretes para conduzir em aula

- **Sempre revise o plano** antes de deixar implementar — é o ponto mais barato para corrigir rumo.
- **Escopo travado:** se o Claude começar a adiantar features de aulas futuras, corte e reaponte para a spec da aula.
- **Chat magro, spec gorda:** precisou explicar muito no chat? Leve isso para a spec ou para o CLAUDE.md.
- **Cuidado com custo de IA:** resumo e classificação chamam a API — reforce cache e limite de conteúdo; nos testes, a IA é sempre mockada.
- **CLAUDE.md ao fim de cada aula:** toda decisão nova vira uma linha lá — é o que faz a aula seguinte "já saber".
- **Commit por aula:** cada incremento fechado é um commit; a spec correspondente entra versionada junto.
