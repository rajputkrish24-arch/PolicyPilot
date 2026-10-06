"""
pdf_parser.py - PDF text extraction for government scheme documents

Downloads and extracts text from scheme PDFs using PyMuPDF (fitz).
Free and open-source - no paid OCR tools.
"""

import fitz  # PyMuPDF
import requests
import os
import json
import re

# Directories
PDF_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "pdfs")
SCHEMES_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "schemes")
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(SCHEMES_DIR, exist_ok=True)


def download_pdf(url, filename=None):
    """
    Download a PDF file from a URL.
    Returns the local file path.
    """
    if not filename:
        # Extract filename from URL
        filename = url.split("/")[-1]
        if not filename.endswith(".pdf"):
            filename += ".pdf"

    filepath = os.path.join(PDF_DIR, filename)

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Downloaded: {filename}")
        return filepath

    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return None


def extract_text_from_pdf(pdf_path):
    """
    Extract all text from a PDF file using PyMuPDF.
    Returns the extracted text as a string.
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF {pdf_path}: {e}")
        return ""

    full_text = ""

    for page_num in range(len(doc)):
        page = doc[page_num]
        # Extract text from the page
        text = page.get_text("text")
        if text:
            full_text += text + "\n"

    doc.close()
    return full_text


def extract_tables_from_pdf(pdf_path):
    """
    Simple table extraction from PDF.
    Uses text positioning to detect tabular data.
    Returns a list of rows (each row is a list of strings).
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF {pdf_path}: {e}")
        return []

    tables = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        # Get text blocks with position info
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" in block:
                row = []
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:
                            row.append(text)
                if row:
                    tables.append(row)

    doc.close()
    return tables


def parse_scheme_pdf(pdf_path):
    """
    Parse a government scheme PDF and extract structured information.
    Returns a dict with scheme details.
    """
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return None

    # Clean up the text
    text = re.sub(r'\s+', ' ', text)

    # Try to identify scheme name (usually in first few lines)
    name = ""
    lines = text.split('\n')
    for line in lines[:5]:
        line = line.strip()
        if len(line) > 5 and len(line) < 200:
            name = line
            break

    # Try to extract sections using keyword matching
    eligibility = extract_section(text, ["eligib", "who can", "target", "beneficiary"])
    benefits = extract_section(text, ["benefit", "assistance", "amount", "subsidy", "cover"])
    documents = extract_section(text, ["document", "proof", "certificate", "required doc"])
    application = extract_section(text, ["apply", "application", "how to", "procedure", "process"])

    scheme = {
        "name": name or os.path.basename(pdf_path).replace(".pdf", ""),
        "url": "",
        "eligibility": eligibility or "Not available from PDF",
        "benefits": benefits or "Not available from PDF",
        "documents_required": documents or "Not available from PDF",
        "application_steps": application or "Not available from PDF",
        "full_text": text,
        "source_pdf": os.path.basename(pdf_path),
    }

    return scheme


def extract_section(text, keywords):
    """
    Extract a section of text that follows any of the given keywords.
    Returns up to 300 characters after the keyword match.
    """
    text_lower = text.lower()
    for keyword in keywords:
        idx = text_lower.find(keyword)
        if idx != -1:
            # Get text starting from the keyword, up to 300 chars
            start = idx
            end = min(start + 400, len(text))
            section = text[start:end].strip()
            # Clean up and return
            section = re.sub(r'\s+', ' ', section)
            return section
    return ""


def process_pdf_directory():
    """
    Process all PDFs in the PDF directory.
    Extract text and save as scheme JSON files.
    """
    schemes = []

    # Check if there are any PDFs to process
    if not os.path.exists(PDF_DIR):
        print("No PDF directory found.")
        return schemes

    pdf_files = [f for f in os.listdir(PDF_DIR) if f.endswith(".pdf")]

    if not pdf_files:
        print("No PDF files found in directory.")
        return schemes

    for pdf_file in pdf_files:
        pdf_path = os.path.join(PDF_DIR, pdf_file)
        print(f"Processing: {pdf_file}")

        scheme = parse_scheme_pdf(pdf_path)
        if scheme:
            schemes.append(scheme)

    # Save parsed schemes
    if schemes:
        output_path = os.path.join(SCHEMES_DIR, "pdf_schemes.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(schemes, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(schemes)} schemes from PDFs to {output_path}")

    return schemes


def merge_scheme_files():
    """
    Merge scraped schemes and PDF-parsed schemes into one file.
    """
    all_schemes = []

    # Load scraped schemes
    scraped_path = os.path.join(SCHEMES_DIR, "schemes.json")
    if os.path.exists(scraped_path):
        with open(scraped_path, "r", encoding="utf-8") as f:
            all_schemes.extend(json.load(f))

    # Load PDF schemes
    pdf_path = os.path.join(SCHEMES_DIR, "pdf_schemes.json")
    if os.path.exists(pdf_path):
        with open(pdf_path, "r", encoding="utf-8") as f:
            all_schemes.extend(json.load(f))

    # Save merged
    merged_path = os.path.join(SCHEMES_DIR, "all_schemes.json")
    with open(merged_path, "w", encoding="utf-8") as f:
        json.dump(all_schemes, f, indent=2, ensure_ascii=False)

    print(f"Merged {len(all_schemes)} total schemes to {merged_path}")
    return all_schemes


if __name__ == "__main__":
    # Process any PDFs in the data/pdfs directory
    pdf_schemes = process_pdf_directory()

    # Merge all scheme sources
    all_schemes = merge_scheme_files()
    print(f"\nTotal schemes available: {len(all_schemes)}")
