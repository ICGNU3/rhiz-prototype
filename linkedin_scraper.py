#!/usr/bin/env python3
"""
LinkedIn Connections Scraper
Extracts contact information from LinkedIn connections page
Target URL: https://www.linkedin.com/mynetwork/invite-connect/connections/
"""

import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import uuid
from datetime import datetime
import psycopg2


class LinkedInConnectionsScraper:
    """
    Scrapes LinkedIn connections page for contact information
    Requires user to be logged in to LinkedIn manually first
    """
    
    def __init__(self, headless=False):
        self.setup_driver(headless)
        self.connections = []
        
    def setup_driver(self, headless=False):
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # User agent to avoid detection
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def navigate_to_connections(self):
        """Navigate to LinkedIn connections page"""
        connections_url = "https://www.linkedin.com/mynetwork/invite-connect/connections/"
        print(f"Navigating to: {connections_url}")
        self.driver.get(connections_url)
        
        # Wait for page to load
        time.sleep(3)
        
        # Check if user is logged in
        if "login" in self.driver.current_url.lower() or "challenge" in self.driver.current_url.lower():
            print("❌ Please log in to LinkedIn first and try again.")
            return False
            
        print("✅ Successfully accessed LinkedIn connections page")
        return True
        
    def scroll_and_load_connections(self, max_connections=500):
        """Scroll page to load all connections"""
        print(f"Loading connections (max: {max_connections})...")
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        connections_loaded = 0
        
        while connections_loaded < max_connections:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait for new content to load
            time.sleep(2)
            
            # Check if we've loaded more connections
            current_connections = self.count_visible_connections()
            if current_connections > connections_loaded:
                connections_loaded = current_connections
                print(f"Loaded {connections_loaded} connections...")
            
            # Calculate new scroll height and compare with last height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("Reached end of connections list")
                break
            last_height = new_height
            
        print(f"✅ Finished loading {connections_loaded} connections")
        return connections_loaded
        
    def count_visible_connections(self):
        """Count currently visible connection cards"""
        try:
            connection_cards = self.driver.find_elements(By.CSS_SELECTOR, "[data-test-app-aware-link]")
            return len(connection_cards)
        except:
            return 0
            
    def extract_connection_data(self):
        """Extract data from all visible connection cards"""
        print("Extracting connection data...")
        
        # LinkedIn connection card selectors (these may need updating as LinkedIn changes their UI)
        connection_selectors = [
            "[data-test-app-aware-link]",  # Main connection cards
            ".mn-connection-card",         # Alternative selector
            ".search-result__wrapper",     # Search result style
        ]
        
        connections_found = []
        
        for selector in connection_selectors:
            try:
                connection_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if connection_elements:
                    print(f"Found {len(connection_elements)} connections using selector: {selector}")
                    connections_found = connection_elements
                    break
            except:
                continue
                
        if not connections_found:
            print("⚠️ No connection elements found. LinkedIn may have updated their HTML structure.")
            return []
            
        extracted_data = []
        
        for i, element in enumerate(connections_found):
            try:
                connection_data = self.extract_single_connection(element, i)
                if connection_data:
                    extracted_data.append(connection_data)
                    
                # Add small delay to avoid overwhelming the page
                if i % 20 == 0:
                    time.sleep(0.5)
                    
            except Exception as e:
                print(f"Error extracting connection {i}: {str(e)}")
                continue
                
        print(f"✅ Successfully extracted {len(extracted_data)} connections")
        return extracted_data
        
    def extract_single_connection(self, element, index):
        """Extract data from a single connection element"""
        try:
            # Try multiple strategies to extract name
            name = self.extract_name(element)
            if not name:
                return None
                
            # Extract other fields
            title = self.extract_title(element)
            company = self.extract_company(element)
            location = self.extract_location(element)
            profile_url = self.extract_profile_url(element)
            
            connection_data = {
                'name': name,
                'title': title or '',
                'company': company or '',
                'location': location or '',
                'profile_url': profile_url or '',
                'connection_date': '',  # LinkedIn doesn't show this on connections page
                'notes': f'LinkedIn connection #{index + 1}',
                'source': 'linkedin_scraper'
            }
            
            return connection_data
            
        except Exception as e:
            print(f"Error extracting connection data: {str(e)}")
            return None
            
    def extract_name(self, element):
        """Extract name using multiple strategies"""
        name_selectors = [
            ".mn-connection-card__name",
            ".search-result__result-link",
            "[data-control-name='connection_profile']",
            ".actor-name",
            ".name",
            "h3",
            ".t-16"
        ]
        
        for selector in name_selectors:
            try:
                name_element = element.find_element(By.CSS_SELECTOR, selector)
                name = name_element.text.strip()
                if name and len(name) > 1:
                    return name
            except:
                continue
                
        return None
        
    def extract_title(self, element):
        """Extract job title"""
        title_selectors = [
            ".mn-connection-card__occupation",
            ".search-result__result-headline",
            ".actor-description",
            ".t-12",
            ".t-black--light"
        ]
        
        for selector in title_selectors:
            try:
                title_element = element.find_element(By.CSS_SELECTOR, selector)
                title = title_element.text.strip()
                if title:
                    return title
            except:
                continue
                
        return ""
        
    def extract_company(self, element):
        """Extract company name from title or separate field"""
        # Often company is part of the title like "Software Engineer at Google"
        title = self.extract_title(element)
        if title and " at " in title:
            parts = title.split(" at ")
            if len(parts) > 1:
                return parts[-1].strip()
                
        # Try dedicated company selectors
        company_selectors = [
            ".mn-connection-card__company",
            ".search-result__result-subline",
        ]
        
        for selector in company_selectors:
            try:
                company_element = element.find_element(By.CSS_SELECTOR, selector)
                company = company_element.text.strip()
                if company:
                    return company
            except:
                continue
                
        return ""
        
    def extract_location(self, element):
        """Extract location information"""
        location_selectors = [
            ".mn-connection-card__location",
            ".search-result__result-location",
            ".actor-meta"
        ]
        
        for selector in location_selectors:
            try:
                location_element = element.find_element(By.CSS_SELECTOR, selector)
                location = location_element.text.strip()
                if location:
                    return location
            except:
                continue
                
        return ""
        
    def extract_profile_url(self, element):
        """Extract LinkedIn profile URL"""
        try:
            link_element = element.find_element(By.TAG_NAME, "a")
            href = link_element.get_attribute("href")
            if href and "linkedin.com/in/" in href:
                return href
        except:
            pass
            
        return ""
        
    def save_to_database(self, connections_data, user_id):
        """Save extracted connections to PostgreSQL database"""
        if not connections_data:
            print("No connections to save")
            return 0
            
        print(f"Saving {len(connections_data)} connections to database...")
        
        try:
            conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
            
            contacts_imported = 0
            
            with conn.cursor() as cursor:
                for connection in connections_data:
                    try:
                        contact_id = str(uuid.uuid4())
                        
                        # Determine warmth level (all LinkedIn connections are at least "warm")
                        warmth_status = 3  # Warm
                        warmth_label = "Warm"
                        
                        cursor.execute('''
                            INSERT INTO contacts (id, user_id, name, email, phone, company, title, 
                                                notes, warmth_status, warmth_label, source, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''', (
                            contact_id,
                            user_id,
                            connection['name'],
                            '',  # email not available from scraping
                            '',  # phone not available
                            connection['company'],
                            connection['title'],
                            f"LinkedIn connection. {connection['notes']}. Profile: {connection['profile_url']}",
                            warmth_status,
                            warmth_label,
                            'linkedin_scraper',
                            datetime.now().isoformat()
                        ))
                        
                        contacts_imported += 1
                        
                    except Exception as e:
                        print(f"Error inserting connection {connection['name']}: {str(e)}")
                        continue
                        
            conn.commit()
            conn.close()
            
            print(f"✅ Successfully imported {contacts_imported} LinkedIn connections")
            return contacts_imported
            
        except Exception as e:
            print(f"Database error: {str(e)}")
            return 0
            
    def export_to_csv(self, connections_data, filename="linkedin_connections.csv"):
        """Export connections to CSV file"""
        if not connections_data:
            print("No connections to export")
            return
            
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'title', 'company', 'location', 'profile_url', 'notes']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for connection in connections_data:
                writer.writerow({
                    'name': connection['name'],
                    'title': connection['title'],
                    'company': connection['company'],
                    'location': connection['location'],
                    'profile_url': connection['profile_url'],
                    'notes': connection['notes']
                })
                
        print(f"✅ Exported {len(connections_data)} connections to {filename}")
        
    def scrape_connections(self, user_id, max_connections=500):
        """Main method to scrape LinkedIn connections"""
        try:
            print("🚀 Starting LinkedIn connections scraping...")
            print("📋 Instructions:")
            print("1. Make sure you're logged into LinkedIn in another browser tab")
            print("2. Visit: https://www.linkedin.com/mynetwork/invite-connect/connections/")
            print("3. This scraper will extract your connection information")
            print()
            
            # Navigate to connections page
            if not self.navigate_to_connections():
                return None
                
            # Load all connections by scrolling
            self.scroll_and_load_connections(max_connections)
            
            # Extract connection data
            connections_data = self.extract_connection_data()
            
            if not connections_data:
                print("❌ No connections found. Please check if you're logged in and the page loaded correctly.")
                return None
                
            # Save to database
            imported_count = self.save_to_database(connections_data, user_id)
            
            # Also export to CSV as backup
            self.export_to_csv(connections_data, f"linkedin_connections_{user_id}.csv")
            
            return {
                'total_scraped': len(connections_data),
                'imported_to_db': imported_count,
                'connections': connections_data
            }
            
        except Exception as e:
            print(f"❌ Scraping failed: {str(e)}")
            return None
            
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Clean up WebDriver"""
        try:
            self.driver.quit()
        except:
            pass


def main():
    """Command line interface for testing"""
    scraper = LinkedInConnectionsScraper(headless=False)
    
    # Test with dummy user ID
    result = scraper.scrape_connections("test_user", max_connections=100)
    
    if result:
        print(f"\n🎉 Scraping completed successfully!")
        print(f"Total scraped: {result['total_scraped']}")
        print(f"Imported to database: {result['imported_to_db']}")
    else:
        print("\n❌ Scraping failed")


if __name__ == "__main__":
    main()