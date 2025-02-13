# test_google.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Path to your ChromeDriver
driver_path = './tests/driver/chromedriver.exe'

# Create a Service object for ChromeDriver
service = Service(driver_path)

# Initialize the Chrome WebDriver
driver = webdriver.Chrome(service=service)

try:
    # Open Google homepage
    driver.get("https://www.google.com")
    
    # Find the search box, input text, and submit
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys("Selenium with Chrome")
    search_box.send_keys(Keys.RETURN)
    
    # Wait for a few seconds to let the results load
    time.sleep(3)
    
    # Print page title to verify the test ran
    print("Page Title: ", driver.title)
    
finally:
    # Close the browser
    driver.quit()
