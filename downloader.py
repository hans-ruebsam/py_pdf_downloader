"""
Script to download all PDF files from a given webpage.
Checks for active virtual environment.
"""
import sys
import argparse
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def ensure_venv():
    """
    Ensure script is run inside a virtual environment.
    """
    if sys.prefix == sys.base_prefix:
        sys.exit("Fehler: Das Skript muss in einem Virtual Environment ausgeführt werden.")


def download_pdfs(url, output_dir):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all links ending with .pdf
    links = [a.get('href') for a in soup.find_all('a', href=True)]
    pdf_links = [urljoin(url, href) for href in links if href.lower().endswith('.pdf')]

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Download each PDF
    for link in pdf_links:
        filename = os.path.basename(link)
        file_path = os.path.join(output_dir, filename)
        with requests.get(link, stream=True) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Downloaded {filename}")


def main():
    ensure_venv()
    parser = argparse.ArgumentParser(
        description="Download all PDF files from a webpage"
    )
    parser.add_argument(
        "url",
        help="URL of the webpage containing PDF links"
    )
    parser.add_argument(
        "-o", "--output",
        default="pdfs",
        help="Output directory for downloaded PDFs"
    )
    args = parser.parse_args()
    download_pdfs(args.url, args.output)

if __name__ == "__main__":
    main()