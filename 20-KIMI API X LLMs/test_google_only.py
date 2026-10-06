"""
Teste de fumaça (smoke test) dos benchmarks usando APENAS o Google Gemini.
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
import google.generativeai as genai

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TEXT_MODEL = "gemini-3.5-flash"
VISION_MODEL = "gemini-3.5-flash"

genai.configure(api_key=GOOGLE_API_KEY)


def call_gemini(system_prompt, user_prompt, model=TEXT_MODEL):
    """Chamada padronizada igual aos notebooks de benchmark."""
    start = time.time()
    gemini_model = genai.GenerativeModel(model)
    response = gemini_model.generate_content(
        [system_prompt, user_prompt],
        generation_config={"temperature": 0.3}
    )
    elapsed = time.time() - start
    usage = response.usage_metadata
    return {
        "content": response.text,
        "input_tokens": usage.prompt_token_count,
        "output_tokens": usage.candidates_token_count,
        "total_tokens": usage.total_token_count,
        "time_seconds": elapsed,
    }


def test_textual():
    print("\n" + "=" * 60)
    print("TESTE 1: Benchmark Textual")
    print("=" * 60)
    system = "Você é um especialista em tecnologia. Responda de forma clara e objetiva."
    user = "Explique o que é um LLM em até 3 frases."
    result = call_gemini(system, user)
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
    result = call_gemini(system, user)
    print(f"✅ Código gerado em {result['time_seconds']:.2f}s")
    print(f"   Tokens: {result['total_tokens']}")

    match = re.search(r"```python\n(.*?)\n```", result["content"], re.DOTALL)
    code = match.group(1).strip() if match else result["content"].strip()

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

    img = Image.new("RGB", (300, 100), color="white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
    except Exception:
        font = ImageFont.load_default()
    draw.text((20, 35), "Gemini Test 2026", fill="black", font=font)

    start = time.time()
    gemini_model = genai.GenerativeModel(VISION_MODEL)
    response = gemini_model.generate_content(
        ["Transcreva o texto desta imagem.", img],
        generation_config={"temperature": 0.3}
    )
    elapsed = time.time() - start
    content = response.text
    print(f"✅ Resposta vision recebida em {elapsed:.2f}s")
    usage = response.usage_metadata
    print(f"   Tokens: {usage.total_token_count}")
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
    result = call_gemini(system, user)
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
    print("🔍 Iniciando smoke tests com Google Gemini")
    print(f"   Modelo texto: {TEXT_MODEL}")
    print(f"   Modelo visão: {VISION_MODEL}")
    if not GOOGLE_API_KEY or GOOGLE_API_KEY.startswith("sua_chave"):
        print("❌ GOOGLE_API_KEY não configurada no .env")
        return

    try:
        test_textual()
        test_code()
        test_multimodal()
        test_automation()
        print("\n" + "=" * 60)
        print("✅ TODOS OS TESTES CONCLUÍDOS COM GOOGLE GEMINI")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ ERRO DURANTE OS TESTES: {e}")
        raise


if __name__ == "__main__":
    main()
