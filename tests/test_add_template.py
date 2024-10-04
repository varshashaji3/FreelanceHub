from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
try:
    driver.get('http://127.0.0.1:8000/login/')
    email_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, 'mail'))
    )
    email_input.send_keys('admin@gmail.com')
    password_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, 'pass'))
    )
    password_input.send_keys('Admin@12')
    password_input.send_keys(Keys.RETURN)
    WebDriverWait(driver, 10).until(EC.url_contains('/administrator/admin_view/'))
    print("Logged in successfully. Current URL:", driver.current_url)
    
    driver.get('http://127.0.0.1:8000/administrator/add_template/')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'project_form')))
    
    # Fill in the form details
    title_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'title'))
    )
    title_input.send_keys('Template2')
    
    file_input1 = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'template_file')))
    file_input1.send_keys('C:/Users/LENOVO/Downloads/index.html')
    
    file_input2 = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'cover_image')))
    file_input2.send_keys('C:/Users/LENOVO/Downloads/openstack.pdf')
    
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(4)
    
    # Check if the submit button is disabled
    submit_button = driver.find_element(By.ID, 'submit_btn')
    if submit_button.get_attribute('disabled'):
        driver.execute_script("alert('Test Passed: Submit button is disabled.Due to error in form filling');")
    else:
        # Click the submit button if it is enabled
        submit_button.click()
        # Wait for redirection to the template list page
        WebDriverWait(driver, 10).until(EC.url_contains('/administrator/template_list/'))
        if driver.current_url == 'http://127.0.0.1:8000/administrator/template_list/':
            driver.execute_script("alert('Test Passed: Submit button was enabled and redirected successfully.');")
        else:
            driver.execute_script("alert('Test Failed: Did not redirect to the expected URL.');")

except Exception as e:
    print(f"Test Failed: {e}")

finally:
    time.sleep(3)
    driver.quit()
