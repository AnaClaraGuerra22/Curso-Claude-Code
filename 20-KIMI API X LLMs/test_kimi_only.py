"""
Teste de fumaça (smoke test) dos benchmarks usando APENAS o Kimi.
Verifica se a API responde, se tokens são retornados e se os fluxos
específicos de cada benchmark funcionam.
"""

import os
import io
import re
import base64
import tempfile
import subprocess
import time
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI

load_dotenv()

KIMI_API_KEY = os.getenv("KIMI_API_KEY")
BASE_URL = "https://api.moonshot.ai/v1"
MODEL = "kimi-k3"

client = OpenAI(api_key=KIMI_API_KEY, base_url=BASE_URL)


def call_kimi(system_prompt, user_prompt):
    """Chamada padronizada igual aos notebooks de benchmark."""
    start = time.time()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=1.0,
    )
    elapsed = time.time() - start
    return {
        "content": response.choices[0].message.content,
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
        "time_seconds": elapsed,
    }


def test_textual():
    print("\n" + "=" * 60)
    print("TESTE 1: Benchmark Textual")
    print("=" * 60)
    system = "Você é um especialista em tecnologia. Responda de forma clara e objetiva."
    user = "Explique o que é um LLM em até 3 frases."
    result = call_kimi(system, user)
    print(f"✅ Resposta recebida em {result['time_seconds']:.2f}s")
    print(f"   Tokens: {result['total_tokens']} (in: {result['input_tokens']}, out: {result['output_tokens']})")
    print(f"   Resumo: {result['content'][:200]}...")


def test_code():
    print("\n" + "=" * 60)
    print("TESTE 2: Benchmark de Geração de Código")
    print("=" * 60)
    system = "Você é um desenvolvedor Python sênior. Retorne apenas código, sem explicações."
    user = (
        "Escreva uma função Python chamada `is_prime(n)` que verifica se um número "
        "inteiro é primo. Inclua também 3 testes unitários usando assert."
    )
    result = call_kimi(system, user, temperature=0.2)
    print(f"✅ Código gerado em {result['time_seconds']:.2f}s")
    print(f"   Tokens: {result['total_tokens']}")

    # Extrai código
    match = re.search(r"```python\n(.*?)\n```", result["content"], re.DOTALL)
    code = match.group(1).strip() if match else result["content"].strip()

    # Executa
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        temp_path = f.name

    try:
        proc = subprocess.run(["python", temp_path], capture_output=True, text=True, timeout=10)
        success = proc.returncode == 0
        print(f"   Execução: {'✅ OK' if success else '❌ FALHA'}")
        if not success:
            print(f"   Erro: {proc.stderr[:300]}")
    finally:
        os.unlink(temp_path)


def test_multimodal():
    print("\n" + "=" * 60)
    print("TESTE 3: Benchmark Multimodal")
    print("=" * 60)

    # Cria imagem simples
    img = Image.new("RGB", (300, 100), color="white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
    except Exception:
        font = ImageFont.load_default()
    draw.text((20, 35), "Kimi Test 2026", fill="black", font=font)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    start = time.time()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Transcreva o texto desta imagem."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
            ],
        }],
        temperature=1.0,
    )
    elapsed = time.time() - start
    content = response.choices[0].message.content
    print(f"✅ Resposta vision recebida em {elapsed:.2f}s")
    print(f"   Tokens: {response.usage.total_tokens}")
    print(f"   Texto detectado: {content[:200]}...")


def test_automation():
    print("\n" + "=" * 60)
    print("TESTE 4: Benchmark Automação/Testes/Documentação")
    print("=" * 60)
    system = "Você é um engenheiro de qualidade de software. Gere apenas código Python com testes pytest."
    user = (
        "Crie testes pytest para: def discount_price(price, discount_percent):\n"
        "    if price < 0 or discount_percent < 0 or discount_percent > 100:\n"
        "        raise ValueError('Valores inválidos')\n"
        "    return round(price * (1 - discount_percent / 100), 2)\n"
        "Cobre casos normais e de erro."
    )
    result = call_kimi(system, user)
    print(f"✅ Testes gerados em {result['time_seconds']:.2f}s")
    print(f"   Tokens: {result['total_tokens']}")

    match = re.search(r"```python\n(.*?)\n```", result["content"], re.DOTALL)
    code = match.group(1).strip() if match else result["content"].strip()

    with tempfile.NamedTemporaryFile(mode="w", suffix="_test.py", delete=False) as f:
        f.write(code)
        temp_path = f.name

    try:
        proc = subprocess.run(["python", "-m", "pytest", temp_path, "-v"], capture_output=True, text=True, timeout=30)
        passed = proc.returncode == 0
        print(f"   pytest: {'✅ PASSOU' if passed else '❌ FALHOU'}")
        print(f"   Saída: {proc.stdout[:300]}")
        if not passed:
            print(f"   Erro: {proc.stderr[:300]}")
    finally:
        os.unlink(temp_path)


def main():
    print("🔍 Iniciando smoke tests com Kimi (modelo: %s)" % MODEL)
    if not KIMI_API_KEY or KIMI_API_KEY.startswith("sua_chave"):
        print("❌ KIMI_API_KEY não configurada no .env")
        return

    try:
        test_textual()
        test_code()
        test_multimodal()
        test_automation()
        print("\n" + "=" * 60)
        print("✅ TODOS OS TESTES CONCLUÍDOS COM KIMI")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ ERRO DURANTE OS TESTES: {e}")
        raise


if __name__ == "__main__":
    main()
