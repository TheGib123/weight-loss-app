from flask import Flask, render_template, request, redirect, flash, url_for
from mysql.connector import Error
from dotenv import load_dotenv
import mysql.connector
import pandas as pd
import os
import charts

load_dotenv()
LOSEIT_EMAIL = os.getenv('LOSEIT_EMAIL')
LOSEIT_PASSWORD = os.getenv('LOSEIT_PASSWORD')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
HEIGHT = int(os.getenv('HEIGHT'))
AGE = int(os.getenv('AGE'))
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

def init_db():
    try:
        q ='''
            CREATE TABLE IF NOT EXISTS entries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date DATE UNIQUE,
                calories INT,
                bmr INT,
                weight FLOAT
            )
        '''
        execute_query(q)
    except Error as e:
        print("DB Init Error:", e)

def load_dfs(df_weight, df_calories):
    try:
        # Make sure 'date' column exists and is properly formatted
        df_weight['weight_date'] = pd.to_datetime(df_weight['Date']).dt.date
        df_calories['calorie_date'] = pd.to_datetime(df_calories['Date']).dt.date
        del df_weight['Date']
        del df_calories['Date']

        df = pd.merge(df_weight, df_calories, left_on='weight_date', right_on='calorie_date')
        del df['calorie_date']
        df.rename(columns={'weight_date': 'date', 'Weight':'weight', 'Food Calories':'calories'}, inplace=True)
        df = df.sort_values(by='date')
        df['bmr'] = 10 * (df['weight'] * 0.45359237) + 6.25 * (HEIGHT * 2.54) - 5 * AGE + 5
        df['bmr'] = df['bmr'].round(0).astype(int)

        for _, row in df.iterrows():
            date = row['date']
            calories = row['calories']
            bmr = row['bmr']
            weight = row['weight']
            q = f'REPLACE INTO entries (date, calories, bmr, weight) VALUES ("{date}", {calories}, {bmr}, {weight})'
            execute_query(q)

        flash('CSV imported successfully!', 'success')

    except Exception as e:
        print("CSV Upload Error:", e)
        flash('Error importing CSV: ' + str(e), 'danger')

##############################################################################################
# Flask application to manage weight and calorie entries
##############################################################################################

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route('/upload', methods=['POST'])
def upload_csv():
    weight_file = request.files.get('weight_file')
    calorie_file = request.files.get('calorie_file')

    if not weight_file or not calorie_file:
        flash('Both files are required!', 'danger')
        return redirect('/')

    try:
        # Load both CSVs using pandas
        df_weight = pd.read_csv(weight_file)
        df_calories = pd.read_csv(calorie_file)
        load_dfs(df_weight, df_calories)

    except Exception as e:
        print("CSV Upload Error:", e)
        flash('Error importing CSV: ' + str(e), 'danger')

    return redirect('/')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            q = 'DELETE from entries'
            execute_query(q)
        except Exception as e:
            print("Error:", e)
        return redirect('/') 

    entries = select_all_query('SELECT date, calories, weight, bmr FROM entries ORDER BY date')
    last_date = select_all_query('SELECT max(date) FROM entries')
    current_weight = select_all_query('SELECT weight FROM entries JOIN (SELECT MAX(date) AS max_date FROM entries) AS max_date_table ON entries.date = max_date_table.max_date')

    weight_data = {
        'heaviest_weight': HEAVY_WEIGHT,
        'total_weight_lost': round(HEAVY_WEIGHT - entries[len(entries) - 1][2],2) if entries else 0,
        'last_date': last_date[0][0] if last_date else None,
        'current_weight': current_weight[0][0] if current_weight else None,
    }
    
    return render_template('index.html', entries=entries, weight_data=weight_data)

@app.route('/complex_chart')
def complex_chart():
    df = pd.read_sql_query('SELECT date, calories, weight, bmr FROM entries ORDER BY date', get_connection())
    graph_html = charts.trend_chart(df)
    return render_template('chart.html', graph_html=graph_html)
    #return redirect(url_for('static', filename='advanced_interactive_chart.html'))

@app.route('/simple_chart')
def simple_chart():
    # convert sql query to a dataframe
    df = pd.read_sql_query('SELECT date, calories, weight, bmr FROM entries ORDER BY date', get_connection())
    graph_html = charts.daily_chart(df)
    return render_template('chart.html', graph_html=graph_html)
    #return redirect(url_for('static', filename='simple_interactive_chart.html'))

@app.route('/avg_chart')
def avg_chart():  
    df = pd.read_sql_query('SELECT date, calories, weight, bmr FROM entries ORDER BY date', get_connection())      
    graph_html = charts.weekly_chart(df)
    return render_template('chart.html', graph_html=graph_html)
    #return redirect(url_for('static', filename='simple_week_avg_interactive_chart.html'))

@app.route('/data')
def view_data():
    entries = select_all_query('SELECT date, calories, weight, bmr FROM entries ORDER BY date')
    # load_data_from_site()
    return render_template('data.html', entries=entries)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)