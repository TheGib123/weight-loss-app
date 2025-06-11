from flask import Flask, render_template, request, redirect, flash, url_for
import mysql.connector
from mysql.connector import Error
import pandas as pd
import charts

height = 65   # in inches
age = 29
heavy_weight = 295
# download_path = '/root/Downloads'


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
        df['bmr'] = 10 * (df['weight'] * 0.45359237) + 6.25 * (height * 2.54) - 5 * age + 5
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

# def remove_downloads():
#     # remove all files in download directory
#     for f in os.listdir(download_path):
#         file_path = os.path.join(download_path, f)
#         if os.path.isfile(file_path):
#             os.remove(file_path)

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

# def load_data_from_site():
#     load_dotenv()
#     EMAIL = os.getenv('EMAIL')
#     PASSWORD = os.getenv('PASSWORD')

#     print(f'email: {EMAIL}')
#     print(f'password: {PASSWORD}')

#     options = Options()
#     options.add_argument('--headless=new')  # Use the new headless mode
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--disable-gpu')
#     options.add_argument('--window-size=1920,1080')

#     driver = webdriver.Chrome(options=options)

#     try:
#         driver.get('https://my.loseit.com/login')

#         # Wait for the email field to appear
#         wait = WebDriverWait(driver, 15)
#         email_field = wait.until(EC.presence_of_element_located((By.NAME, 'email')))
#         password_field = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
#         login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Log In")]')))

#         # Fill out form
#         email_field.send_keys(EMAIL)
#         password_field.send_keys(PASSWORD)
#         login_button.click()

#         # Wait for the login to complete by checking the redirect or user element
#         time.sleep(5)  # optional, can be replaced with smarter wait

#         # Go to export URL
#         driver.get('https://www.loseit.com/export/details/weight?days=168')
#         driver.get('https://www.loseit.com/export/details/foodcalories?days=168')

#         time.sleep(10) # Wait for the export to complete, adjust as necessary

#         # get files in download directory
#         files = os.listdir(download_path)
#         print(f'Downloaded files: {files}')

#         weight_file = [f for f in files if 'weight' in f.lower() and f.endswith('.csv')]
#         calorie_file = [f for f in files if 'foodcalories' in f.lower() and f.endswith('.csv')]

#         print(f'Weight file: {weight_file}')
#         print(f'Calorie file: {calorie_file}')

#         df_weight = pd.read_csv(os.path.join(download_path, weight_file[0]))
#         df_calories = pd.read_csv(os.path.join(download_path, calorie_file[0]))

#         print(df_weight.head())
#         print(df_calories.head())

#     finally:
#         print('Closing the browser...')
#         driver.quit()

#         remove_downloads()

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
        'heaviest_weight': heavy_weight,
        'total_weight_lost': round(heavy_weight - entries[len(entries) - 1][2],2) if entries else 0,
        'last_date': last_date[0][0] if last_date else None,
        'current_weight': current_weight[0][0] if current_weight else None,
    }
    
    return render_template('index.html', entries=entries, weight_data=weight_data)

@app.route('/complex_chart')
def complex_chart():
    df = pd.read_sql_query('SELECT date, calories, weight, bmr FROM entries ORDER BY date', get_connection())
    charts.advanced_chart(df)
    return redirect(url_for('static', filename='advanced_interactive_chart.html'))

@app.route('/simple_chart')
def simple_chart():
    # convert sql query to a dataframe
    df = pd.read_sql_query('SELECT date, calories, weight, bmr FROM entries ORDER BY date', get_connection())
    charts.simple_chart(df)
    return redirect(url_for('static', filename='simple_interactive_chart.html'))

@app.route('/avg_chart')
def avg_chart():  
    df = pd.read_sql_query('SELECT date, calories, weight, bmr FROM entries ORDER BY date', get_connection())      
    charts.avg_chart(df)
    return redirect(url_for('static', filename='simple_week_avg_interactive_chart.html'))

@app.route('/data')
def view_data():
    entries = select_all_query('SELECT date, calories, weight, bmr FROM entries ORDER BY date')
    # load_data_from_site()
    return render_template('data.html', entries=entries)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)