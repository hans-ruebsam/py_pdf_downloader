#!/usr/bin/env python3
import os
import sys
import time
import argparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    pkg = str(e).split()[-1].strip("'")
    print(f"Fehlende Abhängigkeit: {pkg}.")
    print(f"Bitte im aktivierten venv installieren: python -m pip install {pkg}")
    sys.exit(1)

def human_readable_size(num_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num_bytes < 1024.0:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} PB"

def find_pdf_links(url):
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.lower().endswith('.pdf'):
            links.add(requests.compat.urljoin(url, href))
    return sorted(links)

def download_file(url, dest_folder):
    local_name = os.path.join(dest_folder, os.path.basename(url))
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    size = 0
    with open(local_name, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                size += len(chunk)
    return size

def main():
    parser = argparse.ArgumentParser(description="Alle PDF-Dateien einer Webseite herunterladen")
    parser.add_argument('url', help="URL der Seite mit PDF-Links")
    parser.add_argument('-o', '--out', default='pdfs', help="Zielordner für Downloads")
    args = parser.parse_args()

    # Virtual-Environment-Check
    if sys.prefix == sys.base_prefix:
        print("Bitte aktiviere zuerst dein Virtual Environment (z.B. env_pdfdownloader).")
        sys.exit(1)

    os.makedirs(args.out, exist_ok=True)

    print(f"Suche PDF-Links auf {args.url} …")
    pdf_links = find_pdf_links(args.url)
    if not pdf_links:
        print("Keine PDF-Links gefunden.")
        return

    print(f"{len(pdf_links)} PDF(s) gefunden. Starte Download…\n")
    start_time = time.time()
    total_bytes = 0

    for idx, link in enumerate(pdf_links, 1):
        try:
            print(f"[{idx}/{len(pdf_links)}] Lade {link} …", end=' ')
            size = download_file(link, args.out)
            total_bytes += size
            print(f"fertig ({human_readable_size(size)})")
        except Exception as e:
            print(f"Fehler: {e}")

    elapsed = time.time() - start_time
    print("\n———— Zusammenfassung ————")
    print(f"Anzahl heruntergeladener Dateien: {len(pdf_links)}")
    print(f"Gesamtgröße: {human_readable_size(total_bytes)}")
    print(f"Benötigte Zeit: {elapsed:.2f} Sekunden")

if __name__ == '__main__':
    main()
