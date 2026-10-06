"""
scraper.py - Web scraper for government welfare scheme data

Scrapes scheme information from government websites:
- Scheme name
- Eligibility criteria
- Benefits
- Required documents
- Application steps

Uses: requests, BeautifulSoup
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import re
from urllib.parse import urljoin

# Base URLs for Indian government scheme portals
SCRAPE_URLS = [
    "https://www.india.gov.in/my-government/schemes",
    "https://www.myscheme.gov.in/",
]

# Output directory for scraped data
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "schemes")
os.makedirs(DATA_DIR, exist_ok=True)


def clean_text(text):
    """Remove extra whitespace and clean up text."""
    if not text:
        return ""
    # Replace multiple spaces/newlines with single space
    text = re.sub(r'\s+', ' ', text.strip())
    return text


def scrape_scheme_page(url):
    """
    Scrape a single scheme page for details.
    Returns a dict with scheme information.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Try to extract scheme name from heading
    name = ""
    for tag in ["h1", "h2", "h3"]:
        heading = soup.find(tag)
        if heading:
            name = clean_text(heading.get_text())
            break

    # Extract all text content from the page
    body = soup.find("div", class_="content") or soup.find("main") or soup.find("body")
    full_text = clean_text(body.get_text()) if body else ""

    # Try to find specific sections using common patterns
    eligibility = ""
    benefits = ""
    documents = ""
    application_steps = ""

    # Search for section headers and extract following content
    sections = soup.find_all(["h2", "h3", "h4", "strong", "b"])
    for section in sections:
        section_text = clean_text(section.get_text()).lower()
        next_content = ""
        # Get the next sibling paragraph or list
        next_elem = section.find_next_sibling()
        if next_elem:
            next_content = clean_text(next_elem.get_text())

        if "eligib" in section_text and not eligibility:
            eligibility = next_content
        elif "benefit" in section_text and not benefits:
            benefits = next_content
        elif "document" in section_text and not documents:
            documents = next_content
        elif "apply" in section_text or "application" in section_text or "how to" in section_text:
            if not application_steps:
                application_steps = next_content

    # If we couldn't find structured sections, use full text for eligibility
    if not eligibility:
        eligibility = full_text[:500] if full_text else "Not available"

    scheme = {
        "name": name or "Unknown Scheme",
        "url": url,
        "eligibility": eligibility or "Not available",
        "benefits": benefits or "Not available",
        "documents_required": documents or "Not available",
        "application_steps": application_steps or "Not available",
        "full_text": full_text,
    }

    return scheme


def scrape_scheme_list(list_url):
    """
    Scrape a page that lists multiple schemes.
    Returns a list of scheme URLs.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(list_url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching list {list_url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = []

    # Find all links that might be scheme pages
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        text = clean_text(a_tag.get_text()).lower()
        # Filter for links that look like scheme pages
        if any(keyword in text for keyword in ["scheme", "yojana", "programme", "mission"]):
            full_url = urljoin(list_url, href)
            links.append(full_url)

    return links


def run_scraper(max_schemes=20):
    """
    Main scraper function.
    Scrapes scheme data and saves to JSON.
    """
    all_schemes = []

    # First, try to get scheme links from list pages
    scheme_urls = []
    for list_url in SCRAPE_URLS:
        print(f"Scanning list page: {list_url}")
        found_links = scrape_scheme_list(list_url)
        scheme_urls.extend(found_links)
        print(f"  Found {len(found_links)} scheme links")

    # Limit the number of schemes to scrape
    scheme_urls = scheme_urls[:max_schemes]

    # Scrape each scheme page
    for i, url in enumerate(scheme_urls):
        print(f"Scraping scheme {i+1}/{len(scheme_urls)}: {url}")
        scheme = scrape_scheme_page(url)
        if scheme and scheme["name"] != "Unknown Scheme":
            all_schemes.append(scheme)

    # If no schemes found from live scraping, use sample data
    if not all_schemes:
        print("No schemes scraped from web. Using sample data.")
        all_schemes = get_sample_schemes()

    # Save scraped data
    output_path = os.path.join(DATA_DIR, "schemes.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_schemes, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(all_schemes)} schemes to {output_path}")
    return all_schemes


def get_sample_schemes():
    """
    Returns sample Indian government scheme data for testing.
    Used when live scraping is unavailable.
    """
    return [
        {
            "name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
            "url": "https://pmkisan.gov.in",
            "eligibility": "Small and marginal farmer families with cultivable land holding up to 2 hectares. Age above 18 years. Income less than Rs 2,00,000 per annum. Not holding any constitutional post. Not a professional tax payer.",
            "benefits": "Rs 6,000 per year in three installments of Rs 2,000 each directly to bank account.",
            "documents_required": "Aadhaar card, Land ownership documents, Bank passbook, Citizenship proof",
            "application_steps": "1. Visit PM-KISAN portal. 2. Click on New Farmer Registration. 3. Enter Aadhaar and land details. 4. Submit and verify.",
            "full_text": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) is a central sector scheme to supplement the financial needs of small and marginal farmers. Under this scheme, Rs 6,000 per year is transferred in three installments directly to the bank accounts of eligible farmers. Eligibility: Small and marginal farmer families with cultivable land holding up to 2 hectares. The farmer must be a citizen of India. Age must be above 18 years. Family income should be less than Rs 2,00,000 per annum. Professionals like doctors, engineers, lawyers, etc. are not eligible. Required documents: Aadhaar card, Land ownership documents, Bank passbook. Application: Visit pmkisan.gov.in, register with Aadhaar and land details.",
            "state": "All India",
            "category": "Farmer",
            "min_age": 18,
            "max_income": 200000,
        },
        {
            "name": "Pradhan Mantri Awas Yojana (PMAY)",
            "url": "https://pmaymis.nic.in",
            "eligibility": "Economically Weaker Section (EWS) with annual income up to Rs 3,00,000. Low Income Group (LIG) with annual income Rs 3,00,001 to Rs 6,00,000. Beneficiary should not own a pucca house. Age above 18 years.",
            "benefits": "Subsidy of Rs 2.67 lakh on home loan interest. Credit linked subsidy up to 6.5% on loan up to Rs 6 lakh for EWS/LIG.",
            "documents_required": "Aadhaar card, Income certificate, Address proof, Bank passbook, Caste certificate (if applicable)",
            "application_steps": "1. Visit PMAY portal. 2. Select category (EWS/LIG). 3. Fill application form. 4. Submit with documents to nearest CSC.",
            "full_text": "Pradhan Mantri Awas Yojana (PMAY) provides credit linked subsidy on home loans for EWS and LIG categories. EWS: annual income up to Rs 3,00,000. LIG: annual income Rs 3,00,001 to Rs 6,00,000. Subsidy of Rs 2.67 lakh on interest. Beneficiary should not own a pucca house in their name or family member's name. Age must be above 18 years. Required documents: Aadhaar, Income certificate, Address proof. Apply at pmaymis.nic.in.",
            "state": "All India",
            "category": "Housing",
            "min_age": 18,
            "max_income": 600000,
        },
        {
            "name": "Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana (AB-PMJAY)",
            "url": "https://pmjay.gov.in",
            "eligibility": "Families listed in SECC 2011 database. No adult member aged 18-59 in the household. Household with at least one disabled member. Rural families with deprivation criteria. Annual income below Rs 5,00,000 for urban areas.",
            "benefits": "Health cover of Rs 5,00,000 per family per year for secondary and tertiary hospitalization. Cashless and paperless access to hospitals.",
            "documents_required": "Aadhaar card, Ration card, SECC ID, Address proof",
            "application_steps": "1. Check eligibility on pmjay.gov.in using Aadhaar. 2. Visit nearest empaneled hospital. 3. Show PMJAY e-card. 4. Get cashless treatment.",
            "full_text": "Ayushman Bharat PMJAY provides health cover of Rs 5,00,000 per family per year. Eligible families from SECC 2011 database. Covers secondary and tertiary hospitalization. Cashless and paperless. Rural families with deprivation criteria eligible. Urban families with income below Rs 5,00,000. Documents: Aadhaar, Ration card, SECC ID. Apply by checking eligibility on pmjay.gov.in.",
            "state": "All India",
            "category": "Health",
            "min_age": 0,
            "max_income": 500000,
        },
        {
            "name": "Sukanya Samriddhi Yojana (SSY)",
            "url": "https://www.nsiindia.gov.in",
            "eligibility": "Girl child below 10 years of age. Must be an Indian citizen. Account can be opened by parent or guardian. Only two accounts per family (one per girl child).",
            "benefits": "Interest rate of 8.2% per annum (quarterly revised). Tax deduction under Section 80C. Maturity period of 21 years or marriage of girl child after 18 years.",
            "documents_required": "Girl child's birth certificate, Parent's Aadhaar card, Address proof, Passport size photo",
            "application_steps": "1. Visit nearest post office or authorized bank. 2. Fill SSY account opening form. 3. Submit birth certificate and KYC documents. 4. Deposit minimum Rs 250.",
            "full_text": "Sukanya Samriddhi Yojana is a savings scheme for girl children below 10 years. Interest rate 8.2% per annum. Tax benefit under Section 80C. Account opened by parent or guardian. Maturity after 21 years or marriage after 18 years. Only two accounts per family. Minimum deposit Rs 250 per year. Documents: Birth certificate, Aadhaar. Apply at post office or bank.",
            "state": "All India",
            "category": "Savings",
            "min_age": 0,
            "max_age": 10,
            "max_income": 99999999,
        },
        {
            "name": "National Pension System - Swavalamban",
            "url": "https://www.npstrust.org.in",
            "eligibility": "Citizens of India aged 18-60 years. Unorganized sector workers. Should not be covered under any statutory social security scheme. Income less than Rs 5,00,000 per annum.",
            "benefits": "Government contribution of Rs 1,000 per year for 5 years. Pension after retirement age. Tax benefits under Section 80CCD.",
            "documents_required": "Aadhaar card, Bank passbook, Address proof, Age proof",
            "application_steps": "1. Visit NPS Trust website. 2. Register with Aadhaar. 3. Choose fund manager. 4. Make minimum contribution of Rs 1,000 per year.",
            "full_text": "NPS Swavalamban is for unorganized sector workers aged 18-60. Government contributes Rs 1,000 per year for 5 years. Pension after retirement. Tax benefits under Section 80CCD. Income should be less than Rs 5,00,000. Not covered under any statutory social security scheme. Documents: Aadhaar, Bank passbook. Apply at npstrust.org.in.",
            "state": "All India",
            "category": "Pension",
            "min_age": 18,
            "max_age": 60,
            "max_income": 500000,
        },
        {
            "name": "Pradhan Mantri Mudra Yojana (PMMY)",
            "url": "https://www.mudra.org.in",
            "eligibility": "Indian citizens aged 18-65 years. Non-corporate, non-farm small/micro enterprises. Loan amount up to Rs 10 lakh. No collateral required for loans up to Rs 10 lakh.",
            "benefits": "Loans under three categories: Shishu (up to Rs 50,000), Kishore (Rs 50,001 to Rs 5,00,000), Tarun (Rs 5,00,001 to Rs 10,00,000). No collateral. Interest rate as per bank norms.",
            "documents_required": "Aadhaar card, Business plan, Address proof, Bank statement, GST registration (if applicable)",
            "application_steps": "1. Approach any bank/MFI/SFB. 2. Fill MUDRA loan application. 3. Submit business plan and documents. 4. Loan disbursed to bank account.",
            "full_text": "Pradhan Mantri Mudra Yojana provides loans up to Rs 10 lakh for non-corporate non-farm enterprises. Three categories: Shishu up to Rs 50,000, Kishore Rs 50,001 to Rs 5,00,000, Tarun Rs 5,00,001 to Rs 10,00,000. No collateral needed. Age 18-65. Indian citizens. Documents: Aadhaar, Business plan. Apply at any bank.",
            "state": "All India",
            "category": "Business",
            "min_age": 18,
            "max_age": 65,
            "max_income": 99999999,
        },
        {
            "name": "Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)",
            "url": "https://www.jansuraksha.gov.in",
            "eligibility": "Indian citizens aged 18-50 years. Must have a savings bank account. Must give auto-debit consent. Annual premium of Rs 436.",
            "benefits": "Life insurance cover of Rs 2,00,000 on death of insured. Affordable premium of Rs 436 per year. Auto-debit from bank account.",
            "documents_required": "Aadhaar card, Bank passbook with auto-debit form, Age proof",
            "application_steps": "1. Visit your bank branch. 2. Fill PMJJBY enrollment form. 3. Give auto-debit consent. 4. Premium deducted from account annually.",
            "full_text": "PMJJBY provides life insurance of Rs 2,00,000 for Rs 436 per year. Age 18-50. Must have savings bank account. Auto-debit consent required. Covers death from any cause. Apply at bank branch. Documents: Aadhaar, Bank passbook.",
            "state": "All India",
            "category": "Insurance",
            "min_age": 18,
            "max_age": 50,
            "max_income": 99999999,
        },
        {
            "name": "Pradhan Mantri Suraksha Bima Yojana (PMSBY)",
            "url": "https://www.jansuraksha.gov.in",
            "eligibility": "Indian citizens aged 18-70 years. Must have a savings bank account. Must give auto-debit consent. Annual premium of Rs 20.",
            "benefits": "Accidental death cover of Rs 2,00,000. Permanent disability cover of Rs 2,00,000. Partial disability cover of Rs 1,00,000. Premium Rs 20 per year.",
            "documents_required": "Aadhaar card, Bank passbook with auto-debit form, Age proof",
            "application_steps": "1. Visit your bank branch. 2. Fill PMSBY enrollment form. 3. Give auto-debit consent. 4. Premium deducted from account annually.",
            "full_text": "PMSBY provides accident insurance. Death cover Rs 2,00,000. Permanent disability Rs 2,00,000. Partial disability Rs 1,00,000. Premium Rs 20 per year. Age 18-70. Savings bank account required. Auto-debit. Apply at bank.",
            "state": "All India",
            "category": "Insurance",
            "min_age": 18,
            "max_age": 70,
            "max_income": 99999999,
        },
        {
            "name": "Pradhan Mantri Shram Yogi Maan-dhan (PM-SYM)",
            "url": "https://www.shramyogi.gov.in",
            "eligibility": "Unorganized workers aged 18-40 years. Monthly income less than Rs 15,000. Should not be covered under any statutory social security scheme. Must have savings bank account and Aadhaar.",
            "benefits": "Monthly pension of Rs 3,000 after age 60. Equal contribution by government. Contribution ranges from Rs 55 to Rs 200 per month based on age.",
            "documents_required": "Aadhaar card, Bank passbook, Income certificate, Age proof",
            "application_steps": "1. Visit nearest Common Service Centre (CSC). 2. Provide Aadhaar and bank details. 3. Pay first month contribution. 4. Receive Shram Yogi card.",
            "full_text": "PM-SYM provides monthly pension of Rs 3,000 after age 60 for unorganized workers. Age 18-40. Monthly income less than Rs 15,000. Not covered under any statutory scheme. Equal government contribution. Contribution Rs 55-200 per month based on age. Documents: Aadhaar, Bank passbook. Apply at CSC.",
            "state": "All India",
            "category": "Pension",
            "min_age": 18,
            "max_age": 40,
            "max_income": 180000,
        },
        {
            "name": "Pradhan Mantri Ujjwala Yojana (PMUY)",
            "url": "https://www.pmuy.gov.in",
            "eligibility": "Women belonging to Below Poverty Line (BPL) families. Must be adult female. Household should not already have LPG connection. Age above 18 years.",
            "benefits": "Free LPG gas connection. Financial assistance of Rs 1,600 per connection. EMI option for stove and refill cost.",
            "documents_required": "Aadhaar card, BPL certificate, Bank passbook, Address proof",
            "application_steps": "1. Visit nearest LPG distributor. 2. Submit BPL certificate and Aadhaar. 3. Fill application form. 4. Receive free LPG connection.",
            "full_text": "PMUY provides free LPG connections to BPL women. Financial assistance Rs 1,600. Must be adult female from BPL family. No existing LPG connection in household. Age above 18. Documents: Aadhaar, BPL certificate. Apply at LPG distributor.",
            "state": "All India",
            "category": "Welfare",
            "min_age": 18,
            "max_income": 100000,
        },
    ]


if __name__ == "__main__":
    schemes = run_scraper()
    print(f"\nTotal schemes collected: {len(schemes)}")
