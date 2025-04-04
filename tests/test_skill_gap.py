from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

try:
    # Login first
    driver.get('http://127.0.0.1:8000/login/')
    email_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, 'mail'))
    )
    email_input.send_keys('vshaji596@gmail.com')
    password_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, 'pass'))
    )
    password_input.send_keys('Ava@1234')
    password_input.send_keys(Keys.RETURN)
    
    try:
        WebDriverWait(driver, 10).until(EC.url_contains('/freelancer/freelancer_view/'))
        
    except Exception as e:
        raise

    driver.get('http://127.0.0.1:8000/freelancer/analyze-skill-gap/')

    try:
        input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "jobRoleInput"))
        )
        analyze_button = driver.find_element(By.ID, "analyzeBtn")
        error_message = driver.find_element(By.ID, "jobRoleError")

        
        input_field.clear()
        input_field.send_keys("Front-end @Developer")
        time.sleep(1)

        if analyze_button.get_attribute('disabled') and error_message.is_displayed():
            print(f"{GREEN}Test Passed: Button disabled and error shown for invalid input 'Front-end @Developer'{RESET}")
        else:
            print(f"{RED}Test Failed: Button should be disabled for invalid input 'Front-end @Developer'{RESET}")

    except Exception as e:
        print(f"{RED}Failed during job role validation tests: {str(e)}{RESET}")
        raise

except Exception as e:
    print(f"{RED}Test Failed with error: {str(e)}{RESET}")
    raise

finally:
    driver.quit()
