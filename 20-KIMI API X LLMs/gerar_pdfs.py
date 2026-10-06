import os
import subprocess
from pathlib import Path

from markdown import markdown
from weasyprint import HTML, CSS

BASE_DIR = Path(__file__).parent

# Estilo básico para os PDFs
CSS_STYLE = """
@page {
    size: A4;
    margin: 2cm;
}
body {
    font-family: "Helvetica", "Arial", sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}
h1 {
    font-size: 20pt;
    color: #1a1a1a;
    border-bottom: 2px solid #333;
    padding-bottom: 0.3cm;
}
h2 {
    font-size: 16pt;
    color: #2a2a2a;
    margin-top: 1cm;
}
h3 {
    font-size: 13pt;
    color: #444;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 0.5cm 0;
}
th, td {
    border: 1px solid #ccc;
    padding: 6px 8px;
    text-align: left;
    font-size: 10pt;
}
th {
    background-color: #f2f2f2;
    font-weight: bold;
}
code {
    font-family: "Courier New", monospace;
    background-color: #f5f5f5;
    padding: 2px 4px;
    border-radius: 3px;
    font-size: 10pt;
}
pre {
    background-color: #f5f5f5;
    padding: 10px;
    border-radius: 5px;
    overflow-x: auto;
    font-size: 9pt;
}
blockquote {
    border-left: 4px solid #ccc;
    margin: 0;
    padding-left: 1cm;
    color: #666;
}
"""


def markdown_to_pdf(md_path: Path, pdf_path: Path):
    """Converte um arquivo Markdown para PDF."""
    md_content = md_path.read_text(encoding="utf-8")
    html_body = markdown(md_content, extensions=["tables", "fenced_code"])
    html_full = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>{md_path.stem}</title>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    HTML(string=html_full, base_url=str(BASE_DIR)).write_pdf(
        str(pdf_path), stylesheets=[CSS(string=CSS_STYLE)]
    )
    print(f"PDF gerado: {pdf_path}")


def notebook_to_pdf(nb_path: Path, pdf_path: Path):
    """Converte um Jupyter Notebook para PDF via HTML intermediário."""
    html_path = nb_path.with_suffix(".html")

    # Converte notebook para HTML com nbconvert
    subprocess.run(
        [
            "jupyter",
            "nbconvert",
            "--to",
            "html",
            "--no-input",  # oculta as células de código
            str(nb_path),
            "--output",
            str(html_path.name),
        ],
        check=True,
        cwd=str(BASE_DIR),
    )

    # Converte HTML para PDF
    HTML(filename=str(html_path)).write_pdf(
        str(pdf_path), stylesheets=[CSS(string=CSS_STYLE)]
    )
    print(f"PDF gerado: {pdf_path}")

    # Remove HTML intermediário
    html_path.unlink()


if __name__ == "__main__":
    # PDF do escopo
    markdown_to_pdf(
        BASE_DIR / "proposta_escopo_aulas_kimi.md",
        BASE_DIR / "proposta_escopo_aulas_kimi.pdf",
    )

    # PDF do notebook de benchmark textual
    notebook_to_pdf(
        BASE_DIR / "benchmark_textual.ipynb",
        BASE_DIR / "benchmark_textual.pdf",
    )

    print("\nGeração de PDFs concluída.")
