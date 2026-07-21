"""Temporary script to examine PDF structure"""
import pdfplumber
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = ROOT / "Previous_yrs_Result"

for pdf_name in sorted(INPUT_DIR.glob("*.pdf")):
    print(f"\n{'='*80}")
    print(f"FILE: {pdf_name.name}")
    print(f"{'='*80}")
    with pdfplumber.open(str(pdf_name)) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        page = pdf.pages[0]
        text = page.extract_text()
        txt = text[:3000] if text else "NO TEXT"
        print(f"First 3000 chars of page 0:\n{txt}")
        tables = page.extract_tables()
        print(f"\nTables on page 0: {len(tables)}")
        if tables:
            for i, t in enumerate(tables[:2]):
                print(f"\nTable {i}: {len(t)} rows")
                for row in t[:5]:
                    print(f"  {row}")
        # Also check page 1
        if len(pdf.pages) > 1:
            page2 = pdf.pages[1]
            text2 = page2.extract_text()
            print(f"\nPage 1 (first 2000 chars):\n{text2[:2000] if text2 else 'NO TEXT'}")

