from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import logging
from datetime import datetime, timedelta
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gym_bot.log'),
        logging.StreamHandler()
    ]
)

class GymReservationBot:
    def __init__(self, config_path='config.json'):
        self.load_config(config_path)
        self.setup_driver()
        
    def load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                self.gym_url = config['gym_url']
                self.username = config['username']
                self.password = config['password']
                self.preferred_times = config['preferred_times']
                self.reservation_day = config.get('reservation_day', 'tomorrow')
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            raise

    def setup_driver(self):
        """Setup Chrome driver with necessary options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def login(self):
        """Login to the gym website"""
        try:
            self.driver.get(self.gym_url)
            
            # Wait for login form and fill credentials
            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            
            username_field.send_keys(self.username)
            password_field.send_keys(self.password)
            
            # Find and click login button
            login_button = self.driver.find_element(By.ID, "login-button")
            login_button.click()
            
            logging.info("Successfully logged in")
            
        except Exception as e:
            logging.error(f"Login failed: {e}")
            raise

    def navigate_to_reservation_page(self):
        """Navigate to the reservation page for the desired date"""
        try:
            # Calculate target date
            if self.reservation_day == 'tomorrow':
                target_date = datetime.now() + timedelta(days=1)
            else:
                target_date = datetime.strptime(self.reservation_day, '%Y-%m-%d')
            
            # Navigate to reservation page (modify selectors according to gym's website)
            calendar_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "calendar-nav"))
            )
            calendar_button.click()
            
            date_button = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//button[@data-date='{target_date.strftime('%Y-%m-%d')}']")
                )
            )
            date_button.click()
            
            logging.info(f"Navigated to reservation page for {target_date.strftime('%Y-%m-%d')}")
            
        except Exception as e:
            logging.error(f"Navigation failed: {e}")
            raise

    def make_reservation(self):
        """Attempt to make a reservation at preferred times"""
        try:
            for preferred_time in self.preferred_times:
                try:
                    # Look for available slot at preferred time
                    slot = self.wait.until(
                        EC.element_to_be_clickable(
                            (By.XPATH, f"//button[contains(@class, 'time-slot') and contains(text(), '{preferred_time}')]")
                        )
                    )
                    
                    # Click the slot and confirm reservation
                    slot.click()
                    
                    confirm_button = self.wait.until(
                        EC.element_to_be_clickable((By.ID, "confirm-reservation"))
                    )
                    confirm_button.click()
                    
                    logging.info(f"Successfully made reservation for {preferred_time}")
                    return True
                    
                except Exception as e:
                    logging.warning(f"Could not book slot at {preferred_time}: {e}")
                    continue
                    
            logging.error("No available slots found at preferred times")
            return False
            
        except Exception as e:
            logging.error(f"Reservation attempt failed: {e}")
            raise

    def run(self):
        """Main execution flow"""
        try:
            self.login()
            self.navigate_to_reservation_page()
            success = self.make_reservation()
            
            if success:
                logging.info("Reservation process completed successfully")
            else:
                logging.warning("Could not make reservation at any preferred time")
                
        except Exception as e:
            logging.error(f"Bot execution failed: {e}")
        finally:
            self.driver.quit()

if __name__ == "__main__":
    bot = GymReservationBot()
    bot.run()