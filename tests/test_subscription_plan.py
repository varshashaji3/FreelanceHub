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
BLUE = '\033[94m'
BOLD = '\033[1m'
END = '\033[0m'

def wait_for_element(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )
def wait_for_element_visible(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, value))
    )
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
try:
    driver.get('http://127.0.0.1:8000/login/')
    email_input = wait_for_element(driver, By.NAME, 'mail')
    email_input.send_keys('admin@gmail.com')
    password_input = wait_for_element(driver, By.NAME, 'pass')
    password_input.send_keys('Admin@12')
    password_input.send_keys(Keys.RETURN)
    WebDriverWait(driver, 10).until(EC.url_contains('/administrator/admin_view/'))
    print(f"{GREEN}{BOLD}✓ Logged in successfully.{END}")
    driver.get('http://127.0.0.1:8000/administrator/subscriptions/')
    create_button = wait_for_element(driver, By.CLASS_NAME, 'btn-primary')
    create_button.click()
    time.sleep(2) 
    print(f"\n{BLUE}{BOLD}Testing Form Validation:{END}")
    plan_name = wait_for_element(driver, By.ID, 'planName')
    price = wait_for_element(driver, By.ID, 'price')
    duration = wait_for_element(driver, By.ID, 'duration')
    create_plan_button = wait_for_element_visible(driver, By.CLASS_NAME, 'swal2-confirm')
    plan_name.clear()
    plan_name.send_keys('Basic') 
    price.clear()
    price.send_keys('100') 
    duration.clear()
    duration.send_keys('30') 
    client_features = driver.find_elements(By.CLASS_NAME, 'client-feature')
    freelancer_features = driver.find_elements(By.CLASS_NAME, 'freelancer-feature')
    client_features[0].click() 
    freelancer_features[0].click()
    time.sleep(2)  
    if create_plan_button.get_attribute('disabled'):
        print(f"{GREEN}{BOLD}✓ Test Passed: Create Plan button is enabled with valid data.{END}")
    else:
        print(f"{RED}{BOLD}✗ Test Failed: Create Plan button is disabled despite valid data.{END}")
except Exception as e:
    print(f"{RED}{BOLD}✗ Test Failed: {str(e)}{END}")
    
finally:
    driver.quit()

