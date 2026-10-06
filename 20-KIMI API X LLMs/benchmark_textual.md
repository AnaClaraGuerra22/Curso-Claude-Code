# Aula 4 — Benchmark Textual entre Modelos

Este notebook compara **Kimi**, **Claude Opus**, **GPT-4o** e **Gemini** em tarefas textuais.

**Objetivo:** medir custo, tempo e qualidade das respostas para o mesmo prompt.

**Métricas:**
- Tokens de entrada e saída
- Tempo de resposta
- Custo estimado
- Qualidade da resposta (avaliação manual)

## 1. Instalação das dependências

Descomente e execute a linha abaixo caso ainda não tenha instalado.


```python
# !pip install openai anthropic google-generativeai python-dotenv pandas matplotlib
```

## 2. Configuração do ambiente


```python
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# Clientes das APIs
import openai
import anthropic
import google.generativeai as genai

load_dotenv()

KIMI_API_KEY = os.getenv("KIMI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Inicialização dos clientes
kimi_client = openai.OpenAI(api_key=KIMI_API_KEY, base_url="https://api.moonshot.ai/v1")
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
genai.configure(api_key=GOOGLE_API_KEY)
```

## 3. Tabela de preços

Atualize os valores conforme a tabela oficial de cada provider no momento da gravação da aula.


```python
PRICES = {
    "kimi": {"input": 0.50, "output": 2.00},
    "claude-opus": {"input": 15.00, "output": 75.00},
    "gpt-5.5": {"input": 2.50, "output": 10.00},
    "gemini": {"input": 1.25, "output": 5.00},
}
```

## 4. Funções padronizadas de chamada


```python
def call_kimi(system_prompt, user_prompt, model="kimi-k3"):
    start = time.time()
    response = kimi_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=1.0
    )
    elapsed = time.time() - start
    return {
        "provider": "kimi",
        "model": model,
        "response": response.choices[0].message.content,
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
        "time_seconds": elapsed
    }

def call_claude(system_prompt, user_prompt, model="claude-opus-4-6"):
    start = time.time()
    response = anthropic_client.messages.create(
        model=model,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
        temperature=0.3
    )
    elapsed = time.time() - start
    return {
        "provider": "claude-opus",
        "model": model,
        "response": response.content[0].text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
        "time_seconds": elapsed
    }

def call_openai(system_prompt, user_prompt, model="gpt-5.5"):
    start = time.time()
    response = openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )
    elapsed = time.time() - start
    return {
        "provider": "gpt-5.5",
        "model": model,
        "response": response.choices[0].message.content,
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
        "time_seconds": elapsed
    }

def call_gemini(system_prompt, user_prompt, model="gemini-3.5-flash"):
    start = time.time()
    gemini_model = genai.GenerativeModel(model)
    response = gemini_model.generate_content(
        [system_prompt, user_prompt],
        generation_config={"temperature": 0.3}
    )
    elapsed = time.time() - start
    usage = response.usage_metadata
    return {
        "provider": "gemini",
        "model": model,
        "response": response.text,
        "input_tokens": usage.prompt_token_count,
        "output_tokens": usage.candidates_token_count,
        "total_tokens": usage.total_token_count,
        "time_seconds": elapsed
    }
```

## 5. Funções de cálculo de custo e execução do benchmark


```python
def calculate_cost(provider, input_tokens, output_tokens):
    prices = PRICES.get(provider, {})
    input_cost = (input_tokens / 1_000_000) * prices.get("input", 0)
    output_cost = (output_tokens / 1_000_000) * prices.get("output", 0)
    return round(input_cost + output_cost, 6)

def run_textual_benchmark(system_prompt, user_prompt, task_name="tarefa"):
    """
    Executa o mesmo prompt nos 4 modelos e retorna um DataFrame comparativo.
    """
    results = []
    callers = [call_kimi, call_claude, call_openai, call_gemini]
    
    for caller in callers:
        try:
            result = caller(system_prompt, user_prompt)
            result["cost_usd"] = calculate_cost(
                result["provider"],
                result["input_tokens"],
                result["output_tokens"]
            )
            result["task"] = task_name
            results.append(result)
        except Exception as e:
            results.append({
                "provider": caller.__name__.replace("call_", ""),
                "model": "error",
                "response": str(e),
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "time_seconds": 0,
                "cost_usd": 0,
                "task": task_name
            })
    
    df = pd.DataFrame(results)
    return df[["task", "provider", "model", "input_tokens", "output_tokens", "total_tokens", "time_seconds", "cost_usd"]]

def display_responses(df):
    for _, row in df.iterrows():
        print(f"\n{'='*60}")
        print(f"PROVIDER: {row['provider'].upper()} | MODEL: {row['model']}")
        print(f"TOKENS: {row['total_tokens']} | TIME: {row['time_seconds']:.2f}s | COST: ${row['cost_usd']:.6f}")
        print(f"{'='*60}")
        print(row['response'][:800] + "..." if len(row['response']) > 800 else row['response'])
        print()
```

## 6. Benchmark 1 — Resumo de texto técnico


```python
system_prompt = "Você é um especialista em tecnologia. Resuma o texto de forma clara e objetiva, mantendo os pontos técnicos principais."

texto_tecnico = """
Large Language Models (LLMs) são modelos de inteligência artificial baseados na arquitetura Transformer,
treinados com grandes quantidades de texto para prever a próxima palavra em uma sequência. Eles são capazes
de gerar texto, responder perguntas, resumir documentos, traduzir idiomas e auxiliar na programação.
Modelos como GPT-4, Claude, Gemini e Kimi utilizam técnicas como attention mechanisms, fine-tuning e
reinforcement learning from human feedback (RLHF) para melhorar a qualidade das respostas. A escolha de
um LLM para um projeto depende de fatores como custo por token, tamanho de contexto, latência,
multimodalidade e capacidade de seguir instruções complexas.
"""

user_prompt = f"Resuma o seguinte texto em no máximo 3 parágrafos:\n\n{texto_tecnico}"

df_resumo = run_textual_benchmark(system_prompt, user_prompt, task_name="resumo")
df_resumo
```


```python
display_responses(df_resumo)
```

## 7. Benchmark 2 — Explicação de conceito


```python
system_prompt = "Você é um professor de programação. Explique conceitos técnicos de forma simples, com exemplos práticos."

user_prompt = """Explique o que é uma API REST e por que ela é importante no desenvolvimento web.
Use no máximo 200 palavras e inclua um exemplo prático."""

df_conceito = run_textual_benchmark(system_prompt, user_prompt, task_name="explicacao_conceito")
df_conceito
```


```python
display_responses(df_conceito)
```

## 8. Benchmark 3 — Geração de ideias


```python
system_prompt = "Você é um Product Manager experiente. Gere ideias criativas e viáveis para produtos digitais."

user_prompt = """Sugira 3 funcionalidades para um aplicativo de produtividade que use IA para ajudar
desenvolvedores a gerenciar tarefas. Para cada funcionalidade, dê um nome, descreva o problema que resolve
e explique como a IA seria usada."""

df_ideias = run_textual_benchmark(system_prompt, user_prompt, task_name="geracao_ideias")
df_ideias
```


```python
display_responses(df_ideias)
```

## 9. Consolidação dos resultados


```python
df_all = pd.concat([df_resumo, df_conceito, df_ideias], ignore_index=True)
df_all
```

## 10. Visualização comparativa


```python
fig, axes = plt.subplots(1, 3, figsize=(16, 4))

# Custo por tarefa
df_all.pivot(index="provider", columns="task", values="cost_usd").plot.bar(
    ax=axes[0], title="Custo por Tarefa e Provider", rot=0
)
axes[0].set_ylabel("Custo (USD)")

# Tempo por tarefa
df_all.pivot(index="provider", columns="task", values="time_seconds").plot.bar(
    ax=axes[1], title="Tempo de Resposta por Tarefa", rot=0
)
axes[1].set_ylabel("Tempo (s)")

# Tokens de saída por tarefa
df_all.pivot(index="provider", columns="task", values="output_tokens").plot.bar(
    ax=axes[2], title="Tokens de Saída por Tarefa", rot=0
)
axes[2].set_ylabel("Tokens de saída")

plt.tight_layout()
plt.show()
```

## 11. Avaliação de qualidade

Após analisar as respostas, atribua uma nota de 1 a 5 para cada provider em cada tarefa.

Critérios sugeridos:
- Clareza e organização
- Fidelidade ao pedido
- Profundidade técnica
- Concisão


```python
# Exemplo de notas manuais (substitua pelas suas avaliações reais)
quality_scores = {
    ("kimi", "resumo"): 4,
    ("claude-opus", "resumo"): 5,
    ("gpt-5.5", "resumo"): 4,
    ("gemini", "resumo"): 4,
    ("kimi", "explicacao_conceito"): 5,
    ("claude-opus", "explicacao_conceito"): 5,
    ("gpt-5.5", "explicacao_conceito"): 4,
    ("gemini", "explicacao_conceito"): 4,
    ("kimi", "geracao_ideias"): 4,
    ("claude-opus", "geracao_ideias"): 5,
    ("gpt-5.5", "geracao_ideias"): 4,
    ("gemini", "geracao_ideias"): 4,
}

df_all["quality_score"] = df_all.apply(
    lambda row: quality_scores.get((row["provider"], row["task"]), 3), axis=1
)

# Custo-benefício: pontos de qualidade por dólar gasto
df_all["efficiency"] = df_all.apply(
    lambda row: round(row["quality_score"] / max(row["cost_usd"], 0.000001), 2), axis=1
)

df_all[["task", "provider", "cost_usd", "quality_score", "efficiency"]]
```


```python
# Gráfico de custo-benefício
df_efficiency = df_all.pivot(index="provider", columns="task", values="efficiency")
df_efficiency.plot.bar(figsize=(10, 5), title="Custo-Benefício: Qualidade por Dólar", rot=0)
plt.ylabel("Pontos de qualidade / USD")
plt.tight_layout()
plt.show()
```

## 12. Exportação dos resultados


```python
df_all.to_csv("benchmark_textual_resultados.csv", index=False)
print("Resultados salvos em benchmark_textual_resultados.csv")
```

## 13. Conclusão da aula

Com base nos dados coletados, responda:

1. Qual modelo teve o **menor custo** em cada tarefa?
2. Qual modelo teve a **melhor qualidade** de resposta?
3. Qual modelo teve o **melhor custo-benefício**?
4. Em quais cenários o Kimi se mostrou competitivo em relação aos concorrentes?

Use os dados do DataFrame para justificar suas respostas.
