"""
download_scheme_pdfs.py - Download government scheme PDFs for PolicyPilot

Downloads official scheme documents from government websites.
Run this before build_pipeline.py to add more schemes.

Usage:
    python download_scheme_pdfs.py
"""

import requests
import os
from urllib.parse import urlparse

# Directory for downloaded PDFs
PDF_DIR = os.path.join(os.path.dirname(__file__), "data", "pdfs")
os.makedirs(PDF_DIR, exist_ok=True)

# Government scheme PDF URLs (official sources)
SCHEME_PDFS = [
    # PM-KISAN - Farmer Income Support
    {
        "url": "https://pmkisan.gov.in/Documents/PM_Kisan_Scheme_Guidelines.pdf",
        "filename": "PM_KISAN_Guidelines.pdf",
        "name": "Pradhan Mantri Kisan Samman Nidhi",
    },
    # PM Awas Yojana - Housing
    {
        "url": "https://pmaymis.nic.in/upload/PMAY_Guidelines.pdf",
        "filename": "PMAY_Guidelines.pdf",
        "name": "Pradhan Mantri Awas Yojana",
    },
    # PMJJBY - Life Insurance
    {
        "url": "https://www.jansuraksha.gov.in/Documents/PMJJBY_FAQ.pdf",
        "filename": "PMJJBY_FAQ.pdf",
        "name": "Pradhan Mantri Jeevan Jyoti Bima Yojana",
    },
    # PMSBY - Accident Insurance
    {
        "url": "https://www.jansuraksha.gov.in/Documents/PMSBY_FAQ.pdf",
        "filename": "PMSBY_FAQ.pdf",
        "name": "Pradhan Mantri Suraksha Bima Yojana",
    },
    # PM Ujjwala Yojana - LPG Connection
    {
        "url": "https://www.pmuy.gov.in/pdf/faqs.pdf",
        "filename": "PMUY_FAQs.pdf",
        "name": "Pradhan Mantri Ujjwala Yojana",
    },
    # PM Shram Yogi Mandhan - Pension
    {
        "url": "https://www.shramyogi.gov.in/PDF/PM-SYM_Guidelines.pdf",
        "filename": "PM_SYM_Guidelines.pdf",
        "name": "Pradhan Mantri Shram Yogi Maan-dhan",
    },
    # MUDRA Yojana - Loans
    {
        "url": "https://www.mudra.org.in/upload/pdf/Frequently_Asked_Questions.pdf",
        "filename": "MUDRA_FAQ.pdf",
        "name": "Pradhan Mantri Mudra Yojana",
    },
    # Sukanya Samriddhi Yojana - Girl Child Savings
    {
        "url": "https://www.nsiindia.gov.in/writereaddata/FileUpload/13.%20Sukanya%20Samriddhi%20Yojana.pdf",
        "filename": "SSY_Guidelines.pdf",
        "name": "Sukanya Samriddhi Yojana",
    },
    # Ayushman Bharat - Health Insurance
    {
        "url": "https://pmjay.gov.in/sites/default/files/2019-11/AB%20PM-JAY%20Benefits%20Package.pdf",
        "filename": "AB_PMJAY_Benefits.pdf",
        "name": "Ayushman Bharat PMJAY",
    },
    # NPS Tier 1 - Pension
    {
        "url": "https://www.npscra.nsdl.co.in/download/FAQ_NPS_Tier_I.pdf",
        "filename": "NPS_Tier1_FAQ.pdf",
        "name": "National Pension System Tier 1",
    },
    # Kisan Credit Card - Agriculture Loan
    {
        "url": "https://www.nabard.org/pdf/Kisan_Credit_Card_Scheme.pdf",
        "filename": "KCC_Scheme.pdf",
        "name": "Kisan Credit Card",
    },
    # PM Fasal Bima Yojana - Crop Insurance
    {
        "url": "https://pmfby.gov.in/pdf/Farmer_Booklet.pdf",
        "filename": "PMFBY_Booklet.pdf",
        "name": "Pradhan Mantri Fasal Bima Yojana",
    },
    # Stand Up India - Women/SC/ST Entrepreneurs
    {
        "url": "https://www.standupmitra.in/Uploads/ContentFiles/Stand%20Up%20India%20Scheme%20Guidelines.pdf",
        "filename": "StandUp_India_Guidelines.pdf",
        "name": "Stand Up India Scheme",
    },
    # PM SVANidhi - Street Vendors
    {
        "url": "https://pmsvanidhi.mohua.gov.in/pdf/Frequently_Asked_Questions.pdf",
        "filename": "PM_SVANidhi_FAQ.pdf",
        "name": "PM Street Vendor's AtmaNirbhar Nidhi",
    },
]


def download_pdf(url, filename, name):
    """
    Download a single PDF file.
    Returns True if successful, False otherwise.
    """
    filepath = os.path.join(PDF_DIR, filename)
    
    # Skip if already downloaded
    if os.path.exists(filepath):
        print(f"[SKIP] Already exists: {filename}")
        return True
    
    try:
        print(f"[DOWNLOAD] {name}")
        print(f"  URL: {url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=60, stream=True)
        
        # Check if response is actually a PDF
        content_type = response.headers.get('Content-Type', '')
        if 'pdf' not in content_type.lower() and response.headers.get('Content-Disposition', '').endswith('.pdf'):
            # Might be a redirect or error page
            pass
        
        response.raise_for_status()
        
        # Save the PDF
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        file_size = os.path.getsize(filepath)
        print(f"  ✓ Saved: {filename} ({file_size / 1024:.1f} KB)")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Failed: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def download_all_pdfs():
    """
    Download all scheme PDFs.
    """
    print("=" * 60)
    print("PolicyPilot - Government Scheme PDF Downloader")
    print("=" * 60)
    print(f"Download directory: {PDF_DIR}")
    print()
    
    success_count = 0
    failed_count = 0
    
    for scheme in SCHEME_PDFS:
        if download_pdf(scheme["url"], scheme["filename"], scheme["name"]):
            success_count += 1
        else:
            failed_count += 1
        print()
    
    print("=" * 60)
    print("Download Summary")
    print("=" * 60)
    print(f"Successful: {success_count}")
    print(f"Failed: {failed_count}")
    print()
    print("Next steps:")
    print("1. Run: python build_pipeline.py")
    print("2. This will process the PDFs and add them to the RAG index")
    
    return success_count, failed_count


if __name__ == "__main__":
    download_all_pdfs()
