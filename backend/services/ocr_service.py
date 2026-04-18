"""
OCR Service - Extracts text from uploaded medical documents
Supports: PDF, Images (JPG, PNG), Scanned documents
"""

import os
import io
from pathlib import Path
from PIL import Image
import pytesseract
import fitz  # PyMuPDF for PDFs
from typing import Optional

# On Windows, set Tesseract path if needed:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class OCRService:
    """
    Handles text extraction from various document types.
    
    Priority: 
    1. Direct text extraction (for searchable PDFs)
    2. Tesseract OCR (for images and scanned PDFs)
    """

    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Main entry point - extracts text from any supported file type.
        
        Args:
            file_path: Path to the uploaded file
            
        Returns:
            Extracted text as a string
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()

        try:
            if extension == ".pdf":
                return OCRService._extract_from_pdf(str(file_path))
            elif extension in [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"]:
                return OCRService._extract_from_image(str(file_path))
            elif extension == ".txt":
                return file_path.read_text(encoding="utf-8")
            else:
                return f"Unsupported file type: {extension}"
        except Exception as e:
            return f"OCR Error: {str(e)}"

    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        """
        Extract text from PDF.
        First tries direct text extraction (fast).
        Falls back to OCR if PDF is scanned/image-based.
        """
        doc = fitz.open(file_path)
        full_text = []

        for page_num, page in enumerate(doc):
            # Try direct text extraction first
            text = page.get_text("text")

            if text.strip():
                # PDF has real text (not scanned)
                full_text.append(f"--- Page {page_num + 1} ---\n{text}")
            else:
                # PDF is scanned - convert page to image and OCR it
                print(f"Page {page_num + 1} is scanned, using OCR...")
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
                img_bytes = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_bytes))
                ocr_text = pytesseract.image_to_string(img, lang="eng")
                full_text.append(f"--- Page {page_num + 1} (OCR) ---\n{ocr_text}")

        doc.close()
        return "\n".join(full_text)

    @staticmethod
    def _extract_from_image(file_path: str) -> str:
        """
        Extract text from image files using Tesseract OCR.
        Applies preprocessing to improve accuracy.
        """
        img = Image.open(file_path)

        # Convert to RGB if needed (handles RGBA, grayscale, etc.)
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Tesseract OCR with medical document optimized config
        custom_config = r"--oem 3 --psm 6"  # OEM 3 = best, PSM 6 = uniform text block
        text = pytesseract.image_to_string(img, lang="eng", config=custom_config)

        return text

    @staticmethod
    def extract_structured_data(text: str) -> dict:
        """
        Basic regex-based extraction of common lab values from text.
        Used as a fallback when AI extraction fails.
        
        Returns dict of found values.
        """
        import re
        
        patterns = {
            "glucose": r"(?:glucose|blood sugar|fasting glucose)[:\s]+(\d+\.?\d*)\s*(?:mg/dL)?",
            "hba1c": r"(?:hba1c|hemoglobin a1c|glycated)[:\s]+(\d+\.?\d*)\s*%?",
            "cholesterol": r"(?:total cholesterol|cholesterol)[:\s]+(\d+\.?\d*)\s*(?:mg/dL)?",
            "triglycerides": r"(?:triglycerides?)[:\s]+(\d+\.?\d*)\s*(?:mg/dL)?",
            "hdl": r"(?:hdl|good cholesterol)[:\s]+(\d+\.?\d*)\s*(?:mg/dL)?",
            "ldl": r"(?:ldl|bad cholesterol)[:\s]+(\d+\.?\d*)\s*(?:mg/dL)?",
            "hemoglobin": r"(?:hemoglobin|hgb|hb)[:\s]+(\d+\.?\d*)\s*(?:g/dL)?",
            "creatinine": r"(?:creatinine)[:\s]+(\d+\.?\d*)\s*(?:mg/dL)?",
            "blood_pressure_systolic": r"(?:bp|blood pressure)[:\s]+(\d+)/\d+",
            "blood_pressure_diastolic": r"(?:bp|blood pressure)[:\s]+\d+/(\d+)",
        }
        
        extracted = {}
        text_lower = text.lower()
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text_lower)
            if match:
                try:
                    extracted[key] = float(match.group(1))
                except ValueError:
                    pass
        
        return extracted
