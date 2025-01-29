import requests
import sqlite3
import logging
import json
import time
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import feedparser
from typing import Dict, List, Optional
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EDGARCollector:
    def __init__(self, db_path='./data/investsage.db'):
        self.db_path = db_path
        self.sec_base_url = "https://www.sec.gov"
        self.company_facts_url = f"{self.sec_base_url}/Archives/edgar/data"
        self.headers = {
            'User-Agent': 'InvestSage Research Bot (Open Source Project)',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
        # Load CIK lookup data
        self.cik_lookup = self._load_cik_lookup()
        
    def _load_cik_lookup(self) -> Dict[str, str]:
        """
        Loads or creates CIK lookup from ticker symbols to CIK numbers
        """
        try:
            # SEC provides a JSON file mapping tickers to CIKs
            response = requests.get(
                'https://www.sec.gov/files/company_tickers.json',
                headers=self.headers
            )
            response.raise_for_status()
            
            # Lookup dictionary
            cik_data = response.json()
            return {
                company['ticker']: str(company['cik_str']).zfill(10)
                for company in cik_data.values()
            }
            
        except Exception as e:
            logger.error(f"Error loading CIK lookup: {str(e)}")
            return {}
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def get_company_cik(self, symbol: str) -> Optional[str]:
        """
        Gets the CIK number
        """
        return self.cik_lookup.get(symbol.upper())
    
    def get_company_filings_feed(self, cik: str) -> List[Dict]:
        """
        Fetches recent filings
        """
        try:
            feed_url = f"{self.sec_base_url}/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=&output=atom"
            response = requests.get(feed_url, headers=self.headers)
            response.raise_for_status()

            # Parse the RSS feed
            feed = feedparser.parse(response.text)
            
            filings = []
            for entry in feed.entries:
                # Extract filing type from title
                filing_type_match = re.search(r'\((.*?)\)', entry.title)
                if filing_type_match:
                    filing_type = filing_type_match.group(1)
                    
                    filing = {
                        'filing_type': filing_type,
                        'filing_date': datetime(*entry.published_parsed[:6]).isoformat(),
                        'filing_url': entry.link,
                        'title': entry.title,
                        'description': entry.summary
                    }
                    filings.append(filing)
                    

                    time.sleep(0.1)
            
            return filings
            
        except Exception as e:
            logger.error(f"Error fetching filings feed for CIK {cik}: {str(e)}")
            return []
    
    def extract_filing_text(self, filing_url: str) -> Optional[str]:
        """
        Downloads and extracts text from an SEC filing
        """
        try:
            # Get the filing page
            response = requests.get(filing_url, headers=self.headers)
            response.raise_for_status()

            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the actual document link
            doc_link = None
            for link in soup.find_all('a'):
                href = link.get('href', '')
                if href.endswith(('.htm', '.txt')) and '10-' in href:
                    doc_link = href
                    break
            
            if not doc_link:
                return None
                
            # Make sure full URL
            if not doc_link.startswith('http'):
                doc_link = f"{self.sec_base_url}{doc_link}"
            
            # Get the actual document
            time.sleep(0.1)
            doc_response = requests.get(doc_link, headers=self.headers)
            doc_response.raise_for_status()
            
            # Parse and extract text
            doc_soup = BeautifulSoup(doc_response.text, 'html.parser')
            
            # Remove script and style elements
            for script in doc_soup(['script', 'style']):
                script.decompose()

            # Get text content
            text = doc_soup.get_text(separator='\n', strip=True)

            return text

        except Exception as e:
            logger.error(f"Error extracting text from {filing_url}: {str(e)}")
            return None

    def save_filing(self, symbol: str, filing: Dict, extracted_text: Optional[str]):
        """
        Saves a filing to the database
        """
        try:
            with self.get_connection() as conn:
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

        except Exception as e:
            logger.error(f"Error saving filing: {str(e)}")
    
    def collect_filings(self, symbol: str, filing_types: List[str] = None):
        """
        Args:
            symbol: Stock symbol
            filing_types: List of filing types to collect (e.g., ['10-K', '10-Q'])
                        If None, collects all types
        """
        logger.info(f"Collecting SEC filings for {symbol}")
        
        # Get company CIK
        cik = self.get_company_cik(symbol)
        if not cik:
            logger.error(f"Could not find CIK for {symbol}")
            return
        
        # Get filings
        filings = self.get_company_filings_feed(cik)
        
        # Filter by filing type
        if filing_types:
            filings = [f for f in filings if f['filing_type'] in filing_types]
        
        # Process each filing
        for filing in filings:
            logger.info(f"Processing {filing['filing_type']} from {filing['filing_date']}")
            
            # Extract text
            extracted_text = None
            if filing['filing_type'] in ['10-K', '10-Q', '8-K']:
                extracted_text = self.extract_filing_text(filing['filing_url'])
            
            # Save to database
            self.save_filing(symbol, filing, extracted_text)
            
            time.sleep(0.1)
        
        logger.info(f"Completed collecting filings for {symbol}")

if __name__ == "__main__":
    # Example
    collector = EDGARCollector()
    collector.collect_filings("AAPL", filing_types=['10-K', '10-Q', '8-K'])