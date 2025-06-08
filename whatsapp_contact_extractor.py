import os
import time
import random
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from prettytable import PrettyTable

class WhatsAppContactExtractor:
    def __init__(self, user_data_dir):
        """Initialize the WhatsApp contact extractor with Chrome options."""
        self.user_data_dir = os.path.abspath(user_data_dir)
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """Set up undetected Chrome driver with persistent session."""
        options = uc.ChromeOptions()
        
        # Set user data directory with proper path handling
        options.add_argument(f"--user-data-dir={self.user_data_dir}")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        
        # Additional options to make it more undetectable
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-browser-side-navigation")
        options.add_argument("--disable-gpu")
        
        # Initialize the driver with version_main parameter
        self.driver = uc.Chrome(
            options=options,
            version_main=137  # Updated to match your Chrome version
        )

    def wait_for_element(self, by, value, timeout=20):
        """Wait for an element to be present and clickable."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            print(f"Timeout waiting for element: {value}")
            return None

    def human_like_delay(self, min_seconds=1, max_seconds=3):
        """Add random delay to mimic human behavior."""
        time.sleep(random.uniform(min_seconds, max_seconds))

    def scroll_slowly(self, element, scroll_pause_time=1):
        """Scroll through an element slowly to mimic human behavior."""
        last_height = self.driver.execute_script("return arguments[0].scrollHeight", element)
        scroll_attempts = 0
        max_attempts = 50  # Maximum number of scroll attempts
        
        while scroll_attempts < max_attempts:
            # Scroll down
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", element)
            self.human_like_delay(scroll_pause_time, scroll_pause_time + 1)
            
            # Calculate new scroll height
            new_height = self.driver.execute_script("return arguments[0].scrollHeight", element)
            
            # Break if no more content
            if new_height == last_height:
                # Try one more time after a longer delay
                self.human_like_delay(2, 3)
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", element)
                self.human_like_delay(2, 3)
                final_height = self.driver.execute_script("return arguments[0].scrollHeight", element)
                if final_height == new_height:
                    break
            
            last_height = new_height
            scroll_attempts += 1
            
            # Print progress every 10 attempts
            if scroll_attempts % 10 == 0:
                print(f"Scrolling... Attempt {scroll_attempts}/{max_attempts}")

    def safe_click(self, element, timeout=10):
        """Safely click an element, handling overlays and using JavaScript as fallback."""
        try:
            # Wait for any overlays to disappear
            try:
                overlay = self.driver.find_element(By.XPATH, '//div[@role="dialog"]')
                if overlay.is_displayed():
                    print("Waiting for overlay to disappear...")
                    WebDriverWait(self.driver, timeout).until_not(
                        EC.visibility_of(overlay)
                    )
            except NoSuchElementException:
                pass  # No overlay found, continue

            # Try regular click first
            try:
                element.click()
                return True
            except Exception as e:
                print("Regular click failed, trying JavaScript click...")
                # Try JavaScript click
                self.driver.execute_script("arguments[0].click();", element)
                return True
        except Exception as e:
            print(f"Click failed: {str(e)}")
            return False

    def find_group_by_search(self, group_name):
        """Try to find the group using the search box."""
        try:
            # Wait for the search box to be present
            search_box = self.wait_for_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
            if not search_box:
                return False
            
            # Clear and search for the group
            search_box.clear()
            search_box.send_keys(group_name)
            self.human_like_delay(2, 3)
            
            # Wait for search results
            search_results = self.wait_for_element(By.XPATH, '//div[@role="listitem"]')
            if not search_results:
                return False
            
            # Get all search results
            results = self.driver.find_elements(By.XPATH, '//div[@role="listitem"]')
            
            # Check each result for exact match
            for result in results:
                try:
                    title_span = result.find_element(By.XPATH, './/span[@title]')
                    result_name = title_span.get_attribute('title').strip()
                    
                    if result_name == group_name.strip():
                        print(f"Found group in search: {result_name}")
                        if self.safe_click(result):
                            self.human_like_delay(2, 3)
                            return True
                except NoSuchElementException:
                    continue
            
            return False
            
        except Exception as e:
            print(f"Error in search: {str(e)}")
            return False

    def find_group_in_sidebar(self, group_name):
        """Try to find the group by scanning the sidebar."""
        try:
            # Get all chat cards in sidebar
            cards = self.driver.find_elements(By.XPATH, '//div[@role="listitem"]')
            
            for card in cards:
                try:
                    title_span = card.find_element(By.XPATH, './/span[@title]')
                    card_name = title_span.get_attribute('title').strip()
                    
                    if card_name == group_name.strip():
                        print(f"Found group in sidebar: {card_name}")
                        if self.safe_click(card):
                            self.human_like_delay(2, 3)
                            return True
                except NoSuchElementException:
                    continue
            
            return False
            
        except Exception as e:
            print(f"Error scanning sidebar: {str(e)}")
            return False

    def is_right_panel_open(self):
        """Check if the right panel is open by looking for the View all link."""
        try:
            view_all = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    '//div[contains(text(), "View all")]'
                ))
            )
            return view_all.is_displayed()
        except:
            return False

    def click_group_header(self, max_attempts=3):
        """Try multiple methods to click the group header."""
        for attempt in range(max_attempts):
            try:
                print(f"Attempt {attempt + 1} to click group header...")
                
                # First check if right panel is already open
                if self.is_right_panel_open():
                    print("Right panel is already open")
                    return True
                
                # Wait for main div to be present
                main_div = self.wait_for_element(By.ID, 'main', timeout=10)
                if not main_div:
                    print("Main div not found")
                    continue
                
                # Try different methods to find and click the header
                methods = [
                    # Method 1: Click the group name span
                    lambda: self.driver.execute_script(
                        "arguments[0].click();",
                        self.driver.find_element(
                            By.XPATH,
                            '//span[@dir="auto" and contains(@class, "x1iyjqo2")]'
                        )
                    ),
                    
                    # Method 2: Click the header div
                    lambda: self.driver.execute_script(
                        "arguments[0].click();",
                        self.driver.find_element(
                            By.XPATH,
                            '//div[@data-testid="conversation-header"]'
                        )
                    ),
                    
                    # Method 3: Click the profile details button
                    lambda: self.driver.execute_script(
                        "arguments[0].click();",
                        self.driver.find_element(
                            By.XPATH,
                            '//div[@title="Profile details" and @role="button"]'
                        )
                    )
                ]
                
                for method in methods:
                    try:
                        method()
                        self.human_like_delay(2, 3)
                        
                        # Check if right panel opened by looking for View all link
                        if self.is_right_panel_open():
                            print("Successfully opened right panel")
                            return True
                            
                    except Exception as e:
                        print(f"Method failed: {str(e)}")
                        continue
                
                print("All click methods failed, retrying...")
                self.human_like_delay(2, 3)
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                self.human_like_delay(2, 3)
        
        return False

    def extract_contacts(self, group_name):
        """Extract contacts from a WhatsApp group."""
        try:
            # Navigate to WhatsApp Web
            self.driver.get("https://web.whatsapp.com")
            print("Please scan the QR code if not already logged in...")
            
            # Wait for WhatsApp to load (wait for sidebar)
            sidebar = self.wait_for_element(By.XPATH, '//div[@role="listitem"]', timeout=300)
            if not sidebar:
                raise Exception("WhatsApp did not load properly")
            
            print("WhatsApp loaded successfully. Looking for group...")
            self.human_like_delay(2, 4)
            
            # Try to find group using search first
            if not self.find_group_by_search(group_name):
                print("Group not found in search, trying sidebar...")
                if not self.find_group_in_sidebar(group_name):
                    raise Exception(f"Could not find group: {group_name}")
            
            # Wait for chat to load
            self.human_like_delay(3, 5)
            
            # Try to click the group header
            if not self.click_group_header():
                raise Exception("Could not open group info panel")
            
            # Wait for and find the members count element
            members_count = self.wait_for_element(
                By.XPATH,
                '//div[contains(@aria-label, "members")]'
            )
            if not members_count:
                raise Exception("Could not find members count")
            
            # Extract total member count
            total_members = members_count.get_attribute('aria-label').split()[0].replace(',', '')
            print(f"\nTotal members in group: {total_members}")
            
            # Click the View all button
            view_all = self.wait_for_element(
                By.XPATH,
                '//div[contains(text(), "View all")]'
            )
            if not view_all:
                raise Exception("Could not find View all button")
            
            print("Clicking View all button...")
            self.driver.execute_script("arguments[0].click();", view_all)
            self.human_like_delay(2, 3)
            
            # Get participants container
            participants_container = self.wait_for_element(
                By.XPATH,
                '//div[@role="list"]'
            )
            if not participants_container:
                raise Exception("Could not find participants container")
            
            print("\nLoading all contacts (this may take a while)...")
            # Scroll through all participants until no new content loads
            self.scroll_slowly(participants_container)
            
            # Extract contact information
            contacts = []
            participant_elements = self.driver.find_elements(
                By.XPATH,
                '//div[@role="listitem"]'
            )
            
            print(f"\nFound {len(participant_elements)} contacts. Extracting details...")
            
            for i, element in enumerate(participant_elements, 1):
                try:
                    # Try to get name (if present)
                    try:
                        name_span = element.find_element(By.XPATH, './/span[@aria-label]')
                        name = name_span.get_attribute('aria-label').replace('Maybe ', '').strip()
                    except NoSuchElementException:
                        name = "Not available"
                    
                    # Try to get phone number
                    try:
                        # First try to get number from the right side
                        phone_span = element.find_element(By.XPATH, './/span[@class="_ajzr"]//span')
                        phone = phone_span.text.strip()
                    except NoSuchElementException:
                        try:
                            # If not found, try to get from the title attribute
                            phone_span = element.find_element(By.XPATH, './/span[contains(@title, "+")]')
                            phone = phone_span.get_attribute('title').strip()
                        except NoSuchElementException:
                            phone = "Not available"
                    
                    # Check if admin
                    is_admin = bool(element.find_elements(By.XPATH, './/span[contains(text(), "admin")]'))
                    
                    contacts.append({
                        'Name': name,
                        'Phone': phone,
                        'Is Admin': is_admin
                    })
                    
                    # Print progress every 50 contacts
                    if i % 50 == 0:
                        print(f"Processed {i}/{len(participant_elements)} contacts...")
                        
                except NoSuchElementException:
                    continue
            
            print(f"\nSuccessfully extracted {len(contacts)} contacts")
            return contacts
            
        except Exception as e:
            print(f"Error extracting contacts: {str(e)}")
            return []

    def display_contacts(self, contacts):
        """Display contacts in a pretty table format."""
        if not contacts:
            print("No contacts found!")
            return
        
        table = PrettyTable()
        table.field_names = ["Name", "Phone", "Is Admin"]
        
        for contact in contacts:
            table.add_row([
                contact['Name'],
                contact['Phone'],
                "Yes" if contact['Is Admin'] else "No"
            ])
        
        print(table)

    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()

def main():
    # Create user data directory if it doesn't exist
    user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
    os.makedirs(user_data_dir, exist_ok=True)
    
    # Initialize the extractor
    extractor = WhatsAppContactExtractor(user_data_dir)
    
    try:
        # Read group names from CSV
        if not os.path.exists('group.csv'):
            print("Error: group.csv file not found!")
            return
        
        groups = pd.read_csv('group.csv', header=None)[0].tolist()
        
        for group_name in groups:
            print(f"\nExtracting contacts from group: {group_name}")
            contacts = extractor.extract_contacts(group_name)
            extractor.display_contacts(contacts)
            extractor.human_like_delay(2, 4)
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    finally:
        extractor.close()

if __name__ == "__main__":
    main() 