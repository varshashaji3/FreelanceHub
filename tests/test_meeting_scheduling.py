from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
try:
    driver.get('http://127.0.0.1:8000/login/')
    email_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, 'mail')))
    email_input.send_keys('creativedesign@gmail.com')

    password_input = driver.find_element(By.NAME, 'pass')
    password_input.send_keys('Creative@1')
    password_input.send_keys(Keys.RETURN)

    WebDriverWait(driver, 10).until(EC.url_contains('/client/client_view/'))
    driver.get('http://127.0.0.1:8000/client/track_hiring/')
    schedule_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.schedule-btn:not([disabled])')))
    schedule_button.click()
    modal = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'scheduleModal')))
    meeting_link = driver.find_element(By.ID, 'meetingLink')
    meeting_link.clear()
    meeting_link.send_keys('https://google.com/abc-defg-hij') 
    meeting_date = driver.find_element(By.ID, 'meetingDate')
    meeting_date.clear()
    meeting_date.send_keys('02/04/2025 10:00')
    submit_button = driver.find_element(By.ID, 'submitBtn')
    is_disabled = submit_button.get_attribute('disabled')

    if is_disabled is not None: 
        print("✅ Test Passed: Submit button is disabled with an invalid meeting link.")
    else:
        print("❌ Test Failed: Submit button is enabled despite an invalid meeting link.")

except Exception as e:
    print(f"❌ Test Failed: {str(e)}")

finally:
    driver.quit()
