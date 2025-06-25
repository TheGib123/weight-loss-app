from flask import Flask, render_template, request, redirect, flash, url_for
from mysql.connector import Error
from dotenv import load_dotenv
from datetime import datetime
import mysql.connector
import pandas as pd
import os
import sys
import charts


# Import custom helper functions
sys.path.append('../')
import helper_functions as hf


# Load environment variables from .env file
load_dotenv()
HEAVY_WEIGHT = int(os.getenv('HEAVY_WEIGHT'))


# Initialize the database with correct table structure
def init_db():
    try:
        q1 ='''
            CREATE TABLE IF NOT EXISTS entries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date DATE UNIQUE,
                calories INT,
                bmr INT,
                weight FLOAT
            )
        '''
        hf.execute_query(q1)
    except Error as e:
        print("DB Init Error:", e)


##############################################################################################
# Flask application to manage weight and calorie entries
##############################################################################################


app = Flask(__name__)
app.secret_key = 'supersecretkey'


#################
# Home page
#################


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            q = 'DELETE from entries'
            hf.execute_query(q)
        except Exception as e:
            print("Error:", e)
        return redirect('/') 

    entries = hf.select_all_query('SELECT date, calories, weight, bmr FROM entries ORDER BY date')
    last_date = hf.select_all_query('SELECT DATE_FORMAT(MAX(date), "%m/%d/%Y") AS max_date_formatted FROM entries')
    current_weight = hf.select_all_query('SELECT weight FROM entries JOIN (SELECT MAX(date) AS max_date FROM entries) AS max_date_table ON entries.date = max_date_table.max_date')

    weight_data = {
        'heaviest_weight': HEAVY_WEIGHT,
        'total_weight_lost': round(HEAVY_WEIGHT - entries[len(entries) - 1][2],2) if entries else 0,
        'last_date': last_date[0][0] if last_date else None,
        'current_weight': current_weight[0][0] if current_weight else None,
    }
    return render_template('index.html', entries=entries, weight_data=weight_data)


#################
# Data Pages
#################


@app.route('/data')
def view_data():
    entries = hf.select_all_query('SELECT date, calories, weight, bmr FROM entries ORDER BY date')
    return render_template('data.html', entries=entries)


@app.route('/data/import_data', methods=['GET', 'POST'])
def import_data():
    if request.method == 'POST':
        weight_file = request.files.get('weight_file')
        calorie_file = request.files.get('calorie_file')

        if not weight_file or not calorie_file:
            flash('Both files are required!', 'danger')
            return redirect('/data/import_data')

        try:
            # Load both CSVs using pandas
            df_weight = pd.read_csv(weight_file)
            df_calories = pd.read_csv(calorie_file)
            hf.push_dfs_to_db(df_weight, df_calories)
            flash('CSV imported successfully!', 'success')

        except Exception as e:
            print("CSV Upload Error:", e)
            flash('Error importing CSV: ' + str(e), 'danger')
            return redirect('/data/import_data')

        return redirect('/')
    else:
        return render_template('import.html')


#################
# Charts
#################


@app.route('/daily_chart')
def daily_chart():
    df = pd.read_sql_query('SELECT date, calories, weight, bmr FROM entries ORDER BY date', hf.get_connection())
    if (df.empty):
        flash('No data available for chart.', 'danger')
        return redirect('/')
    else:
        graph_html = charts.daily_chart(df)
        return render_template('chart.html', graph_html=graph_html)


@app.route('/weekly_avg_chart')
def weekly_avg_chart():  
    df = pd.read_sql_query('SELECT date, calories, weight, bmr FROM entries ORDER BY date', hf.get_connection())      
    if (df.empty):
        flash('No data available for chart.', 'danger')
        return redirect('/')
    else:
        graph_html = charts.weekly_avg_chart(df)
        return render_template('chart.html', graph_html=graph_html)


@app.route('/calories_distribution') 
def calories_distribution():
    df = pd.read_sql_query('SELECT date, calories, weight, bmr FROM entries ORDER BY date', hf.get_connection())      
    if (df.empty):
        flash('No data available for chart.', 'danger')
        return redirect('/')
    else:
        graph_html = charts.calories_distribution(df, 100)
        return render_template('chart.html', graph_html=graph_html)
    

@app.route('/forecast_weight_by_date', methods=['GET', 'POST'])
def forecast_weight_by_date():
    df = pd.read_sql_query('SELECT date, calories, weight, bmr FROM entries ORDER BY date', hf.get_connection())      
    if (df.empty):
        flash('No data available for chart.', 'danger')
        return redirect('/')
    else:
        if request.method == 'POST':
            forecast_date = request.form.get('forecast_date')
            forecast_date = datetime.strptime(forecast_date, "%Y-%m-%d").date()
            now = datetime.now().date()
            if now > forecast_date:
                flash('Forecast date must be in the future!', 'danger')
                return redirect('/forecast_weight_by_date')
            else:
                graph_html, target_date, predicted_weight = charts.forecast_weight_by_date(df, forecast_date)
                return render_template('chart.html', graph_html=graph_html, forecast_weight_by_date=True, target_date=target_date, predicted_weight=predicted_weight)
            
        else:    
            graph_html, target_date, predicted_weight = charts.forecast_weight_by_date(df)
            return render_template('chart.html', graph_html=graph_html, forecast_weight_by_date=True, target_date=target_date, predicted_weight=predicted_weight)


@app.route('/forecast_date_by_weight', methods=['GET', 'POST'])
def forecast_date_by_weight():
    df = pd.read_sql_query('SELECT date, calories, weight, bmr FROM entries ORDER BY date', hf.get_connection()) 
    min_weight = hf.select_all_query('SELECT min(weight) FROM entries')[0][0];   
    min_weight = int(min_weight)
    if (df.empty):
        flash('No data available for chart.', 'danger')
        return redirect('/')
    else: 
        if request.method == 'POST':
            try:
                target_weight = int(request.form.get('target_weight'))
                graph_html, goal_date = charts.forecast_date_by_weight(df, target_weight)
                return render_template('chart.html', graph_html=graph_html, min_weight=min_weight, forecast_date_by_weight=True, target_weight=target_weight, goal_date=goal_date)
            except:
                pass
        current_weight = hf.select_all_query('SELECT weight FROM entries JOIN (SELECT MAX(date) AS max_date FROM entries) AS max_date_table ON entries.date = max_date_table.max_date')
        current_weight = current_weight[0][0] if current_weight else 110
        target_weight = int(current_weight) - 10
        graph_html, goal_date = charts.forecast_date_by_weight(df, target_weight)
        return render_template('chart.html', graph_html=graph_html, min_weight=min_weight, forecast_date_by_weight=True, target_weight=target_weight, goal_date=goal_date) 


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)