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

class TikTok:
    """Class for TikTok Automation."""
    
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

    def upload_video(self, video_path: str, caption: str) -> bool:
        """Uploads a video to TikTok Reels/Shorts."""
        driver = self.browser
        try:
            info(f"Starting TikTok upload for {self.nickname}...")
            driver.get("https://www.tiktok.com/creator-center/upload")
            time.sleep(10) # Wait for page load
            
            # File Input
            file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            file_input.send_keys(os.path.abspath(video_path))
            info("Video file selected...")
            
            time.sleep(15) # Wait for upload
            
            # Caption (Title)
            # TikTok usually has a contenteditable div for caption
            caption_area = driver.find_element(By.CSS_SELECTOR, "[contenteditable='true']")
            caption_area.click()
            time.sleep(1)
            # Clear and set caption
            caption_area.send_keys(caption)
            info("Caption set...")
            
            time.sleep(5)
            
            # Post Button
            post_btn = driver.find_element(By.CSS_SELECTOR, "button:has-text('Post'), button[data-e2e='post-button']")
            post_btn.click()
            success("TikTok post button clicked!")
            
            time.sleep(10) # Final wait
            driver.quit()
            return True
        except Exception as e:
            error(f"TikTok upload failed: {str(e)}")
            driver.quit()
            return False
