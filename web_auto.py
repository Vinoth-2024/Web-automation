import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Read the Excel file
input_file_path = r"C:\Users\Hacker\OneDrive\Desktop\Credential_Checker-main\Credential_Checker-main\input.xlsx"  # Change the input file path
def read_excel(input_file_path):
    return pd.read_excel(input_file_path)

df = read_excel(input_file_path)

# Specify the full path to the ChromeDriver executable
chrome_driver_path = r"C:\Users\Hacker\OneDrive\Desktop\Credential_Checker-main\chromedriver-win64\chromedriver.exe"  # Update with the full path to chromedriver.exe

# Initialize an empty list to store the working credentials and their status
credentials_status = []

def find_element(driver, by, value, timeout=5):
    try:
        element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value)))
        return element
    except:
        return None

# Initialize a new Chrome webdriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # Optional: Open browser in maximized mode
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Iterate over each row in the dataframe
for index, row in df.iterrows():
    url = row['URL']
    username = row['Username']
    password = row['Password']

    # Open the URL
    driver.get(url)

    try:
        # Find the username and password fields using their IDs
        username_field = find_element(driver, By.ID, 'username_temp', timeout=3)
        password_field = find_element(driver, By.ID, 'password_temp', timeout=3)

        if username_field and password_field:
            # Enter the credentials
            username_field.send_keys(username)
            password_field.send_keys(password)

            # Submit the form by clicking the image button
            submit_button = find_element(driver, By.CSS_SELECTOR, 'input[type="image"]', timeout=3)
            if submit_button:
                submit_button.click()

                # Check if login was successful by looking for specific strings in the response
                try:
                    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'logout') or contains(text(), 'logged in')]")))
                    logging.info(f"Login successful for {username}")
                    credentials_status.append({'Username': username, 'Password': password, 'Login Status': 'Login successful'})
                    # Reset session cookies without quitting the browser
                    driver.delete_all_cookies()
                except:
                    logging.info(f"Login failed for {username}")
                    credentials_status.append({'Username': username, 'Password': password, 'Login Status': 'Login failed'})
                    driver.get(url)  # Reload the website if login failed
            else:
                logging.error(f"Submit button not found for {username}")
                credentials_status.append({'Username': username, 'Password': password, 'Login Status': 'Login failed'})
                driver.get(url)  # Reload the website if login failed
        else:
            logging.error(f"Username or password field not found for {username}")
            credentials_status.append({'Username': username, 'Password': password, 'Login Status': 'Login failed'})
            driver.get(url)  # Reload the website if login failed
    except Exception as e:
        logging.error(f"An error occurred for {username}: {e}")
        credentials_status.append({'Username': username, 'Password': password, 'Login Status': 'Login failed'})
        driver.get(url)  # Reload the website if login failed

# Quit the browser instance after all login attempts
driver.quit()

# Convert the credentials status list to a DataFrame
credentials_status_df = pd.DataFrame(credentials_status)

# Save the credentials status to "working_credentials.xlsx" with the specified column headings
credentials_status_df.columns = ['username', 'password', 'login status']
credentials_status_df.to_excel("working_credentials.xlsx", index=False, startrow=0)

logging.info("Credentials status has been saved to working_credentials.xlsx")
