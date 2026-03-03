import time
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from datetime import datetime
from config import *
from status import *

class Facebook:
    """Class for Facebook Reels Automation."""
    
    def __init__(self, account_uuid: str, nickname: str, profile_path: str, niche: str):
        self.uuid = account_uuid
        self.nickname = nickname
        self.profile_path = profile_path
        self.niche = niche
        
        self.options = Options()
        if get_headless():
            self.options.add_argument("--headless")
        
        if not os.path.exists(self.profile_path):
            raise ValueError(f"Profile path {self.profile_path} does not exist")
            
        self.options.add_argument("-profile")
        self.options.add_argument(self.profile_path)
        
        self.service = Service(GeckoDriverManager().install())
        self.browser = webdriver.Firefox(service=self.service, options=self.options)

    def upload_reel(self, video_path: str, caption: str) -> bool:
        """Uploads a Reel to Facebook."""
        driver = self.browser
        try:
            info(f"Starting Facebook Reel upload for {self.nickname}...")
            driver.get("https://www.facebook.com/reels/create/")
            time.sleep(10) # Wait for page load
            
            # File Input (Facebook use standard file input for Reels create)
            file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            file_input.send_keys(os.path.abspath(video_path))
            info("Reel file selected...")
            
            time.sleep(15) # Wait for upload
            
            # Caption
            caption_area = driver.find_element(By.CSS_SELECTOR, "div[aria-label='Describe your reel...'], div[contenteditable='true']")
            caption_area.click()
            time.sleep(1)
            caption_area.send_keys(caption)
            info("Caption set...")
            
            time.sleep(5)
            
            # Next Button
            next_btn = driver.find_element(By.CSS_SELECTOR, "div[aria-label='Next']")
            next_btn.click()
            info("Next button clicked...")
            
            time.sleep(5)
            
            # Publish Button
            publish_btn = driver.find_element(By.CSS_SELECTOR, "div[aria-label='Publish'], div[aria-label='Share']")
            publish_btn.click()
            success("Facebook publish button clicked!")
            
            time.sleep(10) # Final wait
            driver.quit()
            return True
        except Exception as e:
            error(f"Facebook upload failed: {str(e)}")
            driver.quit()
            return False
