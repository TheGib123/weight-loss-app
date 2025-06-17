from mysql.connector import Error
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import os
import mysql.connector


load_dotenv()
LOSEIT_EMAIL = os.getenv('LOSEIT_EMAIL')
LOSEIT_PASSWORD = os.getenv('LOSEIT_PASSWORD')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME') 
DOB = os.getenv('DOB')
HEIGHT = int(os.getenv('HEIGHT'))
HEAVY_WEIGHT = int(os.getenv('HEAVY_WEIGHT'))
CRON_TIME = os.getenv('CRON_TIME')
DOWNLOAD_PATH = os.getenv('DOWNLOAD_PATH')


def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        database=DB_NAME
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


def get_age(weigh_in_date):
    dob = datetime.strptime(DOB, '%m/%d/%Y')
    age = weigh_in_date.year - dob.year - ((weigh_in_date.month, weigh_in_date.day) < (dob.month, dob.day))
    return age


def push_dfs_to_db(df_weight, df_calories):
    df_weight['weight_date'] = pd.to_datetime(df_weight['Date']).dt.date
    df_calories['calorie_date'] = pd.to_datetime(df_calories['Date']).dt.date
    del df_weight['Date']
    del df_calories['Date']

    df = pd.merge(df_weight, df_calories, left_on='weight_date', right_on='calorie_date')
    del df['calorie_date']
    df.rename(columns={'weight_date': 'date', 'Weight':'weight', 'Food Calories':'calories'}, inplace=True)
    df = df.sort_values(by='date')
    df['age'] = df['date'].apply(get_age)
    print(df.head())
    df['bmr'] = 10 * (df['weight'] * 0.45359237) + 6.25 * (HEIGHT * 2.54) - 5 * df['age'] + 5
    #df['bmr'] = 10 * (df['weight'] * 0.45359237) + 6.25 * (HEIGHT * 2.54) - 5 * 29 + 5
    df['bmr'] = df['bmr'].round(0).astype(int)

    for _, row in df.iterrows():
        date = row['date']
        calories = row['calories']
        bmr = row['bmr']
        weight = row['weight']
        q = f'REPLACE INTO entries (date, calories, bmr, weight) VALUES ("{date}", {calories}, {bmr}, {weight})'
        execute_query(q)