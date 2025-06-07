from flask import Flask, render_template, request, redirect, flash, url_for
import mysql.connector
from mysql.connector import Error
import pandas as pd
import charts

height = 65   # in inches
age = 29
heavy_weight = 295


app = Flask(__name__)
app.secret_key = 'supersecretkey'

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

@app.route('/upload', methods=['POST'])
def upload_csv():
    weight_file = request.files.get('weight_file')
    calorie_file = request.files.get('calorie_file')
    print('a')

    if not weight_file or not calorie_file:
        flash('Both files are required!', 'danger')
        return redirect('/')

    try:
        # Load both CSVs using pandas
        df_weight = pd.read_csv(weight_file)
        df_calories = pd.read_csv(calorie_file)

        print('b')

        # Make sure 'date' column exists and is properly formatted
        df_weight['date'] = pd.to_datetime(df_weight['Date']).dt.date
        df_calories['date'] = pd.to_datetime(df_calories['Date']).dt.date

        print('c')

        df = pd.merge(df_weight, df_calories, on='Date')
        df['Str_Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values(by='Date')
        df['BMR'] = 10 * (df['Weight'] * 0.45359237) + 6.25 * (height * 2.54) - 5 * age + 5
        df['BMR'] = df['BMR'].round(0).astype(int)

        print(df.head())
        print(df.dtypes)

        print('d')

        charts.advanced_chart(df)
        charts.simple_chart(df)
        charts.avg_chart(df)

        print('e')

        for _, row in df.iterrows():
            date = row['Str_Date']
            calories = row['Food Calories']
            bmr = row['BMR']
            weight = row['Weight']
            q = f'REPLACE INTO entries (date, calories, bmr, weight) VALUES ("{date}", {calories}, {bmr}, {weight})'
            execute_query(q)

        print('f')

        flash('CSV imported successfully!', 'success')

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

    conn = get_connection()
    cursor = conn.cursor()  
    cursor.execute('SELECT date, calories, weight, bmr FROM entries ORDER BY date')
    entries = cursor.fetchall()
    cursor.close()
    conn.close()


    weight_data = {
        'heaviest_weight': heavy_weight,
        'total_weight_lost': round(heavy_weight - entries[len(entries) - 1][2],2) if entries else 0,
    }
    
    return render_template('index.html', entries=entries, weight_data=weight_data)

@app.route('/complex_chart')
def complex_chart():
    return redirect(url_for('static', filename='advanced_interactive_chart.html'))

@app.route('/simple_chart')
def simple_chart():
    return redirect(url_for('static', filename='simple_interactive_chart.html'))

@app.route('/avg_chart')
def avg_chart():
    return redirect(url_for('static', filename='simple_week_avg_interactive_chart.html'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
