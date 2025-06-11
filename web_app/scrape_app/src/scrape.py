from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mysql.connector
from mysql.connector import Error
import pandas as pd
import time
from dotenv import load_dotenv
import os

load_dotenv()
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
download_path = os.getenv('DOWNLOAD_PATH')
height = int(os.getenv('HEIGHT'))
age = int(os.getenv('AGE'))

options = Options()
options.add_argument('--headless=new')  # Use the new headless mode
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

driver = webdriver.Chrome(options=options)

def remove_downloads():
    # remove all files in download directory
    for f in os.listdir(download_path):
        file_path = os.path.join(download_path, f)
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
    email_field.send_keys(EMAIL)
    password_field.send_keys(PASSWORD)
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
    files = os.listdir(download_path)
    print(f'Downloaded files: {files}')

    weight_file = [f for f in files if 'weight' in f.lower() and f.endswith('.csv')]
    calorie_file = [f for f in files if 'foodcalories' in f.lower() and f.endswith('.csv')]

    print(f'Weight file: {weight_file}')
    print(f'Calorie file: {calorie_file}')

    df_weight = pd.read_csv(os.path.join(download_path, weight_file[0]))
    df_calories = pd.read_csv(os.path.join(download_path, calorie_file[0]))

    return df_weight, df_calories

def get_connection():
    return mysql.connector.connect(
        host='mysql',
        user='chace',
        password='password',
        database='mydb'
    )

def execute_query(query):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print("Query Error:", e)

def select_all_query(query):
    try:
        conn = get_connection()
        cursor = conn.cursor()  
        cursor.execute(query)
        entries = cursor.fetchall()
        cursor.close()
        conn.close()
        return entries
    except Error as e:
        print("Query Error:", e)

def push_dfs_to_df(df_weight, df_calories):
    df_weight['weight_date'] = pd.to_datetime(df_weight['Date']).dt.date
    df_calories['calorie_date'] = pd.to_datetime(df_calories['Date']).dt.date
    del df_weight['Date']
    del df_calories['Date']

    df = pd.merge(df_weight, df_calories, left_on='weight_date', right_on='calorie_date')
    del df['calorie_date']
    df.rename(columns={'weight_date': 'date', 'Weight':'weight', 'Food Calories':'calories'}, inplace=True)
    df = df.sort_values(by='date')
    df['bmr'] = 10 * (df['weight'] * 0.45359237) + 6.25 * (height * 2.54) - 5 * age + 5
    df['bmr'] = df['bmr'].round(0).astype(int)

    for _, row in df.iterrows():
        date = row['date']
        calories = row['calories']
        bmr = row['bmr']
        weight = row['weight']
        q = f'REPLACE INTO entries (date, calories, bmr, weight) VALUES ("{date}", {calories}, {bmr}, {weight})'
        execute_query(q)


try:
    print('Starting the scraping process...')
    print(pd.Timestamp.now())
    try:
        remove_downloads()   # downloads folder may or may not exsit on first run
    except Exception as e:
        print(f'Error removing downloads: {e}')

    download_files()
    df_weight, df_calories = convert_files_to_df()
    print(df_weight.head())
    print(df_calories.head())
    push_dfs_to_df(df_weight, df_calories)
    print('Scraping process completed successfully.')

except Exception as e:
    print(f'An error occurred: {e}')