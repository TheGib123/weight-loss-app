from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from mysql.connector import Error
from datetime import datetime
from dotenv import load_dotenv
import mysql.connector
import pandas as pd
import time
import os
import helper_functions as hf

load_dotenv()
LOSEIT_EMAIL = os.getenv('LOSEIT_EMAIL')
LOSEIT_PASSWORD = os.getenv('LOSEIT_PASSWORD')
# DB_USERNAME = os.getenv('DB_USERNAME')
# DB_PASSWORD = os.getenv('DB_PASSWORD')
# DB_HOST = os.getenv('DB_HOST')
# DB_NAME = os.getenv('DB_NAME') 
# HEIGHT = int(os.getenv('HEIGHT'))
# AGE = int(os.getenv('AGE'))
# HEAVY_WEIGHT = int(os.getenv('HEAVY_WEIGHT'))
# CRON_TIME = os.getenv('CRON_TIME')
DOWNLOAD_PATH = os.getenv('DOWNLOAD_PATH')

options = Options()
options.add_argument('--headless=new')  # Use the new headless mode
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')

driver = webdriver.Chrome(options=options)

def remove_downloads():
    # remove all files in download directory
    for f in os.listdir(DOWNLOAD_PATH):
        file_path = os.path.join(DOWNLOAD_PATH, f)
        if os.path.isfile(file_path):
            os.remove(file_path)

def download_files():
    driver.get('https://my.loseit.com/login')

    # Wait for the email field to appear
    wait = WebDriverWait(driver, 15)
    email_field = wait.until(EC.presence_of_element_located((By.NAME, 'email')))
    password_field = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Log In")]')))

    # Fill out form
    email_field.send_keys(LOSEIT_EMAIL)
    password_field.send_keys(LOSEIT_PASSWORD)
    login_button.click()

    # Wait for the login to complete by checking the redirect or user element
    time.sleep(5)  # optional, can be replaced with smarter wait

    # Go to export URL
    driver.get('https://www.loseit.com/export/details/weight?days=168')
    driver.get('https://www.loseit.com/export/details/foodcalories?days=168')

    time.sleep(15) # Wait for the export to complete, adjust as necessary
    driver.quit()

def convert_files_to_df():
    # get files in download directory
    files = os.listdir(DOWNLOAD_PATH)
    print(f'Downloaded files: {files}')

    weight_file = [f for f in files if 'weight' in f.lower() and f.endswith('.csv')]
    calorie_file = [f for f in files if 'foodcalories' in f.lower() and f.endswith('.csv')]

    print(f'Weight file: {weight_file}')
    print(f'Calorie file: {calorie_file}')

    df_weight = pd.read_csv(os.path.join(DOWNLOAD_PATH, weight_file[0]))
    df_calories = pd.read_csv(os.path.join(DOWNLOAD_PATH, calorie_file[0]))

    return df_weight, df_calories


try:
    print(f'Date and time: {datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")}')
    print('Starting the scraping process...')
    try:
        print('Removing old downloads...')
        remove_downloads()   # downloads folder may or may not exsit on first run
    except Exception as e:
        print(f'Error removing downloads: {e}')

    print('Downloading files from LoseIt...')
    download_files()

    print('Converting downloaded files to DataFrames...')
    df_weight, df_calories = convert_files_to_df()

    print('Pushing DataFrames to MySQL database...')
    hf.push_dfs_to_db(df_weight, df_calories)

    print('Scraping process completed successfully.')
    print()

except Exception as e:
    print(f'An error occurred: {e}')