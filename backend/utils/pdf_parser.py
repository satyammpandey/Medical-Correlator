# backend/utils/pdf_parser.py
# ============================================
# PDF PARSER
# Extracts text from PDF files
# ============================================

import fitz  # PyMuPDF - fastest PDF library
import pdfplumber  # Better for tables
from pathlib import Path
from loguru import logger


async def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract all text from a PDF file.
    
    Tries PyMuPDF first (fast), falls back to pdfplumber (better for complex PDFs)
    """
    try:
        return _extract_with_pymupdf(file_path)
    except Exception as e:
        logger.warning(f"PyMuPDF failed, trying pdfplumber: {e}")
        try:
            return _extract_with_pdfplumber(file_path)
        except Exception as e2:
            logger.error(f"Both PDF extractors failed: {e2}")
            return ""


def _extract_with_pymupdf(file_path: str) -> str:
    """Fast PDF text extraction using PyMuPDF (fitz)"""
    doc = fitz.open(file_path)
    text_parts = []

    for page_num, page in enumerate(doc):
        text = page.get_text("text")  # Get plain text
        if text.strip():
            text_parts.append(f"--- Page {page_num + 1} ---\n{text}")

    doc.close()
    return "\n".join(text_parts)


def _extract_with_pdfplumber(file_path: str) -> str:
    """Extract text including tables using pdfplumber"""
    text_parts = []

    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            # Extract regular text
            text = page.extract_text()
            if text:
                text_parts.append(f"--- Page {page_num + 1} ---\n{text}")

            # Extract tables (lab reports often have tables)
            tables = page.extract_tables()
            for table in tables:
                if table:
                    table_text = "\n".join([
                        " | ".join([str(cell or "") for cell in row])
                        for row in table
                    ])
                    text_parts.append(f"[TABLE]\n{table_text}\n[/TABLE]")

    return "\n".join(text_parts)
