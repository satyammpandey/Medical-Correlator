# backend/utils/ocr_processor.py
# ============================================
# OCR PROCESSOR
# Extracts text from images and scanned documents
# Uses Tesseract OCR (open source, works well for printed text)
# ============================================

import pytesseract
from PIL import Image
from pathlib import Path
from loguru import logger


async def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from an image using OCR (Optical Character Recognition).
    
    Works on:
    - Photos of medical reports
    - Scanned documents  
    - JPG, PNG, TIFF images
    
    Args:
        image_path: Path to the image file
    
    Returns:
        Extracted text as string
    """
    try:
        logger.info(f"🔍 OCR processing: {image_path}")

        # Open image
        image = Image.open(image_path)

        # Preprocessing for better OCR accuracy
        # Convert to RGB if needed (some images are RGBA or grayscale)
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # OCR with medical document optimization
        # --psm 6 = Assume a single uniform block of text
        # --oem 3 = Use LSTM neural network (best accuracy)
        custom_config = r'--oem 3 --psm 6 -l eng'

        text = pytesseract.image_to_string(image, config=custom_config)

        logger.success(f"✅ OCR extracted {len(text)} characters from {Path(image_path).name}")
        return text.strip()

    except pytesseract.TesseractNotFoundError:
        logger.error("❌ Tesseract not installed! Install: sudo apt install tesseract-ocr")
        logger.error("   Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        return ""

    except Exception as e:
        logger.error(f"❌ OCR failed for {image_path}: {e}")
        return ""
