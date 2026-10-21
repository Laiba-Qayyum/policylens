from pathlib import Path

import pytest
from docx import Document

from src.loaders import load_file


def make_pdf(path: Path, pages: list[str]) -> None:
    # Writes a tiny valid PDF by hand, one text line per page (test helper only).
    objs = ["<< /Type /Catalog /Pages 2 0 R >>"]
    kids = " ".join(f"{4 + 2 * i} 0 R" for i in range(len(pages)))
    objs.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>")
    objs.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    for i, text in enumerate(pages):
        objs.append(
            "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] "
            f"/Contents {5 + 2 * i} 0 R /Resources << /Font << /F1 3 0 R >> >> >>"
        )
        stream = f"BT /F1 12 Tf 20 100 Td ({text}) Tj ET"
        objs.append(f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream")
    out, offsets = "%PDF-1.4\n", []
    for n, body in enumerate(objs, 1):
        offsets.append(len(out))
        out += f"{n} 0 obj\n{body}\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n"
    out += "".join(f"{o:010d} 00000 n \n" for o in offsets)
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF"
    path.write_bytes(out.encode("latin-1"))


def test_txt_is_one_page(tmp_path: Path):
    file = tmp_path / "policy.txt"
    file.write_text("Returns within 30 days.", encoding="utf-8")
    assert load_file(file) == [(1, "Returns within 30 days.")]


def test_unsupported_type_is_rejected(tmp_path: Path):
    file = tmp_path / "notes.xyz"
    file.write_text("hello", encoding="utf-8")
    with pytest.raises(ValueError):
        load_file(file)


def test_missing_file_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_file(tmp_path / "nope.txt")


def test_docx_is_one_page(tmp_path: Path):
    file = tmp_path / "handbook.docx"
    doc = Document()
    doc.add_paragraph("Leave policy")
    doc.add_paragraph("Employees get 20 days.")
    doc.save(str(file))
    assert load_file(file) == [(1, "Leave policy\nEmployees get 20 days.")]


def test_pdf_has_one_entry_per_page(tmp_path: Path):
    file = tmp_path / "rules.pdf"
    make_pdf(file, ["Page one text", "Page two text"])
    assert load_file(file) == [(1, "Page one text"), (2, "Page two text")]
