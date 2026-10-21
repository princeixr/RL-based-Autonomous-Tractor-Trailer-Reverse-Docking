#!/usr/bin/env python3
"""Render the concise project proposal Markdown as a two-page PostScript file."""

from pathlib import Path
import re
import textwrap


PROPOSAL_DIR = Path(__file__).resolve().parent
SOURCE = PROPOSAL_DIR / "two-page-proposal.md"
OUTPUT = PROPOSAL_DIR / "two-page-proposal.ps"

PAGE_WIDTH = 612
PAGE_HEIGHT = 792
LEFT = 46
RIGHT = 566
TOP = 754
BOTTOM = 38
BODY_SIZE = 8.8
BODY_LEADING = 10.4
BODY_CHARS = 107


def ascii_text(value: str) -> str:
    replacements = {
        "–": "-",
        "—": "-",
        "“": '"',
        "”": '"',
        "’": "'",
        "‘": "'",
        "→": "->",
        "φ": "phi",
        "θ": "theta",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value.encode("ascii", "ignore").decode("ascii")


def ps_escape(value: str) -> str:
    return ascii_text(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def strip_markdown(value: str) -> str:
    value = re.sub(r"\*\*(.*?)\*\*", r"\1", value)
    value = re.sub(r"\*(.*?)\*", r"\1", value)
    value = re.sub(r"`(.*?)`", r"\1", value)
    return value.strip()


class PSWriter:
    def __init__(self) -> None:
        self.commands: list[str] = []
        self.page = 0
        self.y = TOP
        self.page_ends: list[float] = []

    def line(self, text: str, x: float, y: float, font: str, size: float, color=(0, 0, 0)) -> None:
        r, g, b = color
        self.commands.append(
            f"{r} {g} {b} setrgbcolor /{font} findfont {size} scalefont setfont "
            f"{x:.1f} {y:.1f} moveto ({ps_escape(text)}) show"
        )

    def rule(self, y: float) -> None:
        self.commands.append(
            f"0.10 0.32 0.48 setrgbcolor 1.2 setlinewidth {LEFT} {y:.1f} moveto {RIGHT} {y:.1f} lineto stroke"
        )

    def start_page(self) -> None:
        if self.page:
            self.finish_page()
        self.page += 1
        self.commands.append(f"%%Page: {self.page} {self.page}")
        self.y = TOP

    def finish_page(self) -> None:
        self.page_ends.append(self.y)
        self.rule(28)
        self.line("Trajectory-Aware RL for Tractor-Trailer Reverse Docking", LEFT, 17, "Helvetica", 7.5, (0.25, 0.25, 0.25))
        self.line(f"Page {self.page} of 2", 520, 17, "Helvetica", 7.5, (0.25, 0.25, 0.25))
        self.commands.append("showpage")

    def title(self, text: str) -> None:
        wrapped = textwrap.wrap(strip_markdown(text), width=58)
        for line in wrapped:
            self.line(line, LEFT, self.y, "Helvetica-Bold", 17.2, (0.07, 0.25, 0.38))
            self.y -= 20
        self.rule(self.y + 4)
        self.y -= 8

    def metadata(self, text: str) -> None:
        self.line(strip_markdown(text), LEFT, self.y, "Helvetica", 8.7, (0.30, 0.30, 0.30))
        self.y -= 11

    def heading(self, text: str) -> None:
        self.y -= 3
        self.line(strip_markdown(text), LEFT, self.y, "Helvetica-Bold", 11.2, (0.07, 0.30, 0.47))
        self.y -= 14

    def paragraph(self, text: str, indent: float = 0, prefix: str = "", space_after: float = 3) -> None:
        text = strip_markdown(text)
        width = BODY_CHARS - int(indent / 5) - len(prefix)
        lines = textwrap.wrap(text, width=max(45, width), break_long_words=False)
        for idx, line in enumerate(lines):
            shown = (prefix if idx == 0 else "") + line
            self.line(shown, LEFT + indent, self.y, "Helvetica", BODY_SIZE)
            self.y -= BODY_LEADING
        self.y -= space_after

    def subheading(self, text: str) -> None:
        self.line(strip_markdown(text), LEFT, self.y, "Helvetica-Bold", 9.4, (0.12, 0.12, 0.12))
        self.y -= 12

    def bullet(self, text: str, number: str | None = None) -> None:
        prefix = f"{number}. " if number else "- "
        self.paragraph(text, indent=11, prefix=prefix, space_after=0.8)

    def table(self, rows: list[list[str]]) -> None:
        for index, row in enumerate(rows):
            if index == 0:
                continue
            label = strip_markdown(row[0])
            content = strip_markdown(row[1])
            self.line(label, LEFT, self.y, "Helvetica-Bold", 8.6)
            wrapped = textwrap.wrap(content, width=82, break_long_words=False)
            for idx, line in enumerate(wrapped):
                self.line(line, LEFT + 68, self.y if idx == 0 else self.y, "Helvetica", 8.6)
                self.y -= 10.4
            self.y -= 2


def render() -> None:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    writer = PSWriter()
    writer.start_page()
    paragraph: list[str] = []
    table_rows: list[list[str]] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            writer.paragraph(" ".join(paragraph))
            paragraph = []

    def flush_table() -> None:
        nonlocal table_rows
        if table_rows:
            writer.table(table_rows)
            table_rows = []

    for raw in lines:
        line = raw.strip()
        if line == "<!-- PAGE BREAK -->":
            flush_paragraph()
            flush_table()
            writer.start_page()
            continue
        if not line:
            flush_paragraph()
            flush_table()
            continue
        if line.startswith("# "):
            flush_paragraph()
            writer.title(line[2:])
        elif line.startswith("## "):
            flush_paragraph()
            flush_table()
            writer.heading(line[3:])
        elif line.startswith("**") and line.endswith("**"):
            flush_paragraph()
            writer.subheading(line[2:-2])
        elif line.startswith("**") and "**" in line[2:]:
            flush_paragraph()
            writer.metadata(line)
        elif re.match(r"^\d+\. ", line):
            flush_paragraph()
            match = re.match(r"^(\d+)\.\s+(.*)$", line)
            assert match
            writer.bullet(match.group(2), match.group(1))
        elif line.startswith("- "):
            flush_paragraph()
            writer.bullet(line[2:])
        elif line.startswith("|") and line.endswith("|"):
            flush_paragraph()
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if not all(re.fullmatch(r"[-: ]+", cell) for cell in cells):
                table_rows.append(cells)
        elif line.startswith("> "):
            flush_paragraph()
            writer.paragraph(line[2:], indent=12, prefix="")
        else:
            paragraph.append(line)

    flush_paragraph()
    flush_table()
    writer.finish_page()

    if writer.page != 2:
        raise SystemExit(f"Expected exactly 2 pages, generated {writer.page}")
    for page_number, end_y in enumerate(writer.page_ends, start=1):
        if end_y < BOTTOM:
            raise SystemExit(f"Page {page_number} overflowed by {BOTTOM - end_y:.1f} points")

    header = [
        "%!PS-Adobe-3.0",
        "%%Creator: project proposal renderer",
        "%%Pages: 2",
        f"%%BoundingBox: 0 0 {PAGE_WIDTH} {PAGE_HEIGHT}",
        "%%EndComments",
    ]
    OUTPUT.write_text("\n".join(header + writer.commands + ["%%EOF", ""]), encoding="ascii")
    cursors = ", ".join(f"p{i}={y:.1f}" for i, y in enumerate(writer.page_ends, start=1))
    print(f"Generated {OUTPUT} with 2 pages; final cursors: {cursors}")


if __name__ == "__main__":
    render()
