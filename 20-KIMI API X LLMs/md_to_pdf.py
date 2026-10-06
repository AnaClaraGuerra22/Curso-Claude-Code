"""
Conversor simples de Markdown para PDF usando fpdf2.
Suporta: headers, parágrafos, listas, tabelas, blocos de código e negrito/itálico.
"""

import re
from pathlib import Path

from fpdf import FPDF


class MarkdownPDF(FPDF):
    def __init__(self):
        super().__init__(unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_margins(15, 15, 15)

        # Fonte Unicode para suportar caracteres especiais em português
        arial_unicode = "/Library/Fonts/Arial Unicode.ttf"
        self.add_font("ArialUnicode", "", arial_unicode, uni=True)
        self.add_font("ArialUnicode", "B", arial_unicode, uni=True)
        self.add_font("ArialUnicode", "I", arial_unicode, uni=True)
        self.add_font("ArialUnicode", "BI", arial_unicode, uni=True)

        # Fonte monoespaçada para código
        courier = "/System/Library/Fonts/Courier.dfont"
        if Path(courier).exists():
            self.add_font("CourierUnicode", "", courier, uni=True)
        else:
            self.add_font("CourierUnicode", "", arial_unicode, uni=True)

        self.set_font("ArialUnicode", "", 11)
        self.line_height = 6

    def add_markdown_text(self, text: str):
        """Renderiza um texto inline com formatação básica de Markdown."""
        # Remove asteriscos duplos (negrito) e itálicos simples
        # FPDF não suporta mistura de fontes em uma célula facilmente,
        # então removemos a marcação e mantemos o texto plano.
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
        text = re.sub(r"\*(.+?)\*", r"\1", text)
        text = text.replace("`", "")
        self.multi_cell(0, self.line_height, text)

    def add_heading(self, text: str, level: int):
        sizes = {1: 18, 2: 14, 3: 12, 4: 11, 5: 10, 6: 10}
        self.ln(4)
        self.set_font("ArialUnicode", "B", sizes.get(level, 11))
        self.multi_cell(0, self.line_height * (1.2 if level <= 2 else 1), text)
        if level <= 2:
            self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.set_font("ArialUnicode", "", 11)
        self.ln(1)

    def add_code_block(self, lines: list[str]):
        self.set_fill_color(240, 240, 240)
        self.set_font("CourierUnicode", "", 9)
        code = "\n".join(lines)
        self.multi_cell(0, 5, code, fill=True)
        self.set_font("ArialUnicode", "", 11)
        self.ln(2)

    def add_table(self, header: list[str], rows: list[list[str]]):
        self.set_font("ArialUnicode", "B", 9)
        col_width = (self.w - self.l_margin - self.r_margin) / len(header)

        # Header
        for cell in header:
            self.cell(col_width, 7, cell, border=1, fill=True)
        self.ln()

        # Rows
        self.set_font("ArialUnicode", "", 9)
        for row in rows:
            for cell in row:
                self.cell(col_width, 7, cell, border=1)
            self.ln()
        self.ln(3)

    def add_bullet_list(self, items: list[str]):
        indent = 6
        for item in items:
            x = self.l_margin + indent
            self.set_x(x)
            self.multi_cell(0, self.line_height, f"• {item}")
        self.ln(1)

    def add_numbered_list(self, items: list[str]):
        indent = 8
        for i, item in enumerate(items, 1):
            x = self.l_margin + indent
            self.set_x(x)
            self.multi_cell(0, self.line_height, f"{i}. {item}")
        self.ln(1)


def parse_markdown(md_path: Path) -> list[dict]:
    """Parseia o markdown em blocos estruturados."""
    content = md_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    blocks = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Headers
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            text = stripped[level:].strip()
            blocks.append({"type": "heading", "level": level, "text": text})
            i += 1
            continue

        # Tabela
        if "|" in stripped and i + 1 < len(lines) and "---" in lines[i + 1]:
            header = [c.strip() for c in stripped.split("|") if c.strip()]
            i += 2  # pula header e separador
            rows = []
            while i < len(lines) and "|" in lines[i].strip():
                row = [c.strip() for c in lines[i].strip().split("|") if c.strip()]
                if row:
                    rows.append(row)
                i += 1
            blocks.append({"type": "table", "header": header, "rows": rows})
            continue

        # Bloco de código
        if stripped.startswith("```"):
            lang = stripped[3:].strip()
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            blocks.append({"type": "code", "lines": code_lines, "lang": lang})
            i += 1
            continue

        # Lista não ordenada
        if stripped.startswith(("- ", "* ")):
            items = []
            while i < len(lines) and lines[i].strip().startswith(("- ", "* ")):
                items.append(lines[i].strip()[2:])
                i += 1
            blocks.append({"type": "bullet_list", "items": items})
            continue

        # Lista ordenada
        match = re.match(r"^(\d+)\.\s+(.+)$", stripped)
        if match:
            items = []
            while i < len(lines):
                m = re.match(r"^(\d+)\.\s+(.+)$", lines[i].strip())
                if m:
                    items.append(m.group(2))
                    i += 1
                else:
                    break
            blocks.append({"type": "numbered_list", "items": items})
            continue

        # Linha horizontal
        if stripped == "---" or set(stripped) == {"-"}:
            blocks.append({"type": "hr"})
            i += 1
            continue

        # Parágrafo
        if stripped:
            para_lines = []
            while i < len(lines) and lines[i].strip():
                para_lines.append(lines[i].strip())
                i += 1
            blocks.append({"type": "paragraph", "text": " ".join(para_lines)})
            continue

        i += 1

    return blocks


def convert_markdown_to_pdf(md_path: Path, pdf_path: Path):
    blocks = parse_markdown(md_path)
    pdf = MarkdownPDF()

    for block in blocks:
        if block["type"] == "heading":
            pdf.add_heading(block["text"], block["level"])
        elif block["type"] == "paragraph":
            pdf.add_markdown_text(block["text"])
            pdf.ln(2)
        elif block["type"] == "bullet_list":
            pdf.add_bullet_list(block["items"])
        elif block["type"] == "numbered_list":
            pdf.add_numbered_list(block["items"])
        elif block["type"] == "code":
            pdf.add_code_block(block["lines"])
        elif block["type"] == "table":
            pdf.add_table(block["header"], block["rows"])
        elif block["type"] == "hr":
            pdf.ln(2)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(2)

    pdf.output(str(pdf_path))
    print(f"PDF gerado: {pdf_path}")


if __name__ == "__main__":
    BASE_DIR = Path(__file__).parent

    convert_markdown_to_pdf(
        BASE_DIR / "proposta_escopo_aulas_kimi.md",
        BASE_DIR / "proposta_escopo_aulas_kimi.pdf",
    )

    convert_markdown_to_pdf(
        BASE_DIR / "benchmark_textual.md",
        BASE_DIR / "benchmark_textual.pdf",
    )
