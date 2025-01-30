import requests
import sqlite3
import logging
import json
import time
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EDGARCollector:
    def __init__(self, db_path='./data/investsage.db'):
        self.db_path = db_path
        self.sec_base_url = "https://www.sec.gov"
        self.headers = {
            'User-Agent': 'InvestSage Research Bot (your@email.com)',
            'Accept-Encoding': 'gzip, deflate',
            'Accept': 'application/json, text/html',
        }
        self.cik_lookup = self._load_cik_lookup()

    def _load_cik_lookup(self) -> Dict[str, str]:
        try:
            url = 'https://www.sec.gov/files/company_tickers.json'
            logger.info(f"Loading CIK lookup from: {url}")
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            lookup = {
                company['ticker']: str(company['cik_str']).zfill(10)
                for company in data.values()
            }
            
            logger.info(f"Loaded {len(lookup)} CIK mappings")
            return lookup
            
        except Exception as e:
            logger.error(f"Error loading CIK lookup: {str(e)}")
            return {}

    def get_company_cik(self, symbol: str) -> Optional[str]:
        return self.cik_lookup.get(symbol.upper())

    def get_company_filings(self, cik: str) -> List[Dict]:
        try:
            # Remove leading zeros from CIK for this endpoint
            cik = cik.lstrip('0')
            
            # Use the company search API
            url = f"{self.sec_base_url}/cgi-bin/browse-edgar"
            params = {
                'CIK': cik,
                'owner': 'exclude',
                'action': 'getcompany',
                'type': '10-',  # This will get both 10-K and 10-Q
                'count': '10',
                'output': 'atom'
            }
            
            logger.info(f"Fetching filings from search API for CIK {cik}")
            
            time.sleep(0.1)  # Rate limiting
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            
            # Parse the XML response
            soup = BeautifulSoup(response.content, 'xml')
            entries = soup.find_all('entry')
            
            filings = []
            for entry in entries:
                # Get the filing type from the title
                title = entry.title.text if entry.title else ''
                if '10-K' in title:
                    filing_type = '10-K'
                elif '10-Q' in title:
                    filing_type = '10-Q'
                else:
                    continue
                
                # Get the filing URL
                filing_url = entry.link['href'] if entry.link else None
                if not filing_url:
                    continue
                
                # Get the filing date
                filing_date = entry.updated.text[:10] if entry.updated else ''
                
                filing = {
                    'filing_type': filing_type,
                    'filing_date': filing_date,
                    'filing_url': filing_url,
                    'title': title,
                    'description': entry.summary.text if entry.summary else ''
                }
                
                filings.append(filing)
                logger.info(f"Found {filing_type} filing from {filing_date}")
            
            logger.info(f"Found {len(filings)} relevant filings")
            return filings
            
        except Exception as e:
            logger.error(f"Error fetching filings for CIK {cik}: {str(e)}")
            return []

    def extract_filing_text(self, filing_url: str) -> Optional[str]:
        try:
            logger.info(f"Downloading filing from: {filing_url}")
            
            time.sleep(0.1)  # Rate limiting
            response = requests.get(filing_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find the main document
            doc_link = None
            for link in soup.find_all('a'):
                href = link.get('href', '')
                if href.endswith('.htm') and ('10-k' in href.lower() or '10-q' in href.lower()):
                    doc_link = href
                    break
            
            if doc_link:
                if not doc_link.startswith('http'):
                    doc_link = f"{self.sec_base_url}{doc_link}"
                
                # Get the actual document
                time.sleep(0.1)  # Rate limiting
                doc_response = requests.get(doc_link, headers=self.headers)
                doc_response.raise_for_status()
                
                doc_soup = BeautifulSoup(doc_response.content, 'html.parser')
                
                # Remove script and style elements
                for element in doc_soup(['script', 'style']):
                    element.decompose()
                
                text = doc_soup.get_text(separator='\n', strip=True)
                return text
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting text from {filing_url}: {str(e)}")
            return None

    def save_filing(self, symbol: str, filing: Dict, extracted_text: Optional[str]):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR IGNORE INTO sec_filings
                    (symbol, filing_type, filing_date, filing_url, description, extracted_text)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    symbol,
                    filing['filing_type'],
                    filing['filing_date'],
                    filing['filing_url'],
                    filing['description'],
                    extracted_text
                ))
                
                conn.commit()
                logger.info(f"Saved {filing['filing_type']} filing for {symbol}")
                
        except Exception as e:
            logger.error(f"Error saving filing: {str(e)}")

    def collect_filings(self, symbol: str, filing_types: List[str] = None):
        logger.info(f"Collecting SEC filings for {symbol}")
        
        cik = self.get_company_cik(symbol)
        if not cik:
            logger.error(f"Could not find CIK for {symbol}")
            return
        
        logger.info(f"Found CIK: {cik}")
        filings = self.get_company_filings(cik)
        
        if filing_types:
            filings = [f for f in filings if f['filing_type'] in filing_types]
        
        for filing in filings:
            logger.info(f"Processing {filing['filing_type']} from {filing['filing_date']}")
            extracted_text = self.extract_filing_text(filing['filing_url'])
            self.save_filing(symbol, filing, extracted_text)
            time.sleep(0.1)
        
        logger.info(f"Completed collecting filings for {symbol}")

if __name__ == "__main__":
    collector = EDGARCollector()
    collector.collect_filings("AAPL", filing_types=['10-K', '10-Q'])