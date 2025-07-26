import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
import numpy as np
from scipy import stats
from datetime import datetime, timedelta

def daily_trend_chart(df):
    # advanced chart

    fig = go.Figure()

    # Plot Weight on primary y-axis
    fig.add_trace(go.Scatter(
        x=df['date'], 
        y=df['weight'],
        mode='lines+markers',
        name='Weight (lbs)',
        line=dict(color='blue'),
        yaxis='y1'
    ))

    # Weight trend line
    df['str_date'] = pd.to_datetime(df['date'])
    x_numeric = df['str_date'].map(pd.Timestamp.toordinal)
    z = np.polyfit(x_numeric, df['weight'], 1)
    p = np.poly1d(z)
    fig.add_trace(go.Scatter(
        x=df['date'], y=p(x_numeric),
        mode='lines',
        name='Weight Trend',
        line=dict(color='blue', dash='dash'),
        yaxis='y1'
    ))

    # Plot Food Calories on secondary y-axis
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['calories'],
        mode='lines+markers',
        name='Calories',
        line=dict(color='green'),
        yaxis='y2'
    ))

    # Calorie trend line
    z = np.polyfit(x_numeric, df['calories'], 1)
    p = np.poly1d(z)
    fig.add_trace(go.Scatter(
        x=df['date'], y=p(x_numeric),
        mode='lines',
        name='Calorie Trend',
        line=dict(color='green', dash='dash'),
        yaxis='y2'
    ))

    # BMR on secondary y-axis
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['bmr'],
        mode='lines',
        name='BMR',
        line=dict(color='red', dash='dash'),
        yaxis='y2'
    ))

    # Layout and axis formatting
    fig.update_layout(
        title='Daily Weight, Calorie Intake, and BMR',
        xaxis=dict(title='Date'),
        yaxis=dict(
            title=dict(text='Weight (lbs)', font=dict(color='blue')),
            tickfont=dict(color='blue')
        ),
        yaxis2=dict(
            title=dict(text='Calories / BMR', font=dict(color='green')),
            tickfont=dict(color='green'),
            overlaying='y',
            side='right'
        ),
        legend=dict(x=0.5, y=1.15, orientation='h', xanchor='center'),
        margin=dict(t=80),
        hovermode='x unified',
        template='plotly_white'
    )


    # Optional: save to HTML file
    #fig.write_html("static/advanced_interactive_chart.html")

    graph_html = pio.to_html(fig, full_html=False)
    return graph_html

def daily_chart(df):
    # simple chart

    fig = go.Figure()

    # Plot Weight on primary y-axis
    fig.add_trace(go.Scatter(
        x=df['date'], 
        y=df['weight'],
        mode='lines+markers',
        name='Weight (lbs)',
        line=dict(color='blue'),
        yaxis='y1'
    ))

    # Plot Food Calories on secondary y-axis
    fig.add_trace(go.Scatter(
        x=df['date'], 
        y=df['calories'],
        mode='lines+markers',
        name='Calories',
        line=dict(color='green'),
        yaxis='y2'
    ))

    # BMR on secondary y-axis
    fig.add_trace(go.Scatter(
        x=df['date'], 
        y=df['bmr'],
        mode='lines',
        name='BMR',
        line=dict(color='red', dash='dash'),
        yaxis='y2'
    ))

    # Layout and axis formatting
    fig.update_layout(
        title='Daily Weight, Calorie Intake, and BMR',
        xaxis=dict(title='Date'),
        yaxis=dict(
            title=dict(text='Weight (lbs)', font=dict(color='blue')),
            tickfont=dict(color='blue')
        ),
        yaxis2=dict(
            title=dict(text='Calories / BMR', font=dict(color='green')),
            tickfont=dict(color='green'),
            overlaying='y',
            side='right'
        ),
        legend=dict(x=0.5, y=1.15, orientation='h', xanchor='center'),
        margin=dict(t=80),
        hovermode='x unified',
        template='plotly_white'
    )


    # Optional: save to HTML file
    # fig.write_html("static/simple_interactive_chart.html")

    graph_html = pio.to_html(fig, full_html=False)
    return graph_html

def weekly_avg_chart(df):
    week_df = df.copy()
    week_df['date'] = pd.to_datetime(week_df['date'])  # Ensure Date is datetime
    week_df['weekday'] = week_df['date'].dt.day_name()

    monday_found = False
    week_count = 0
    week_group = []

    for index, row in week_df.iterrows():
        if (row['weekday'] != 'Monday' and monday_found == False):
            week_group.append(week_count)
        elif row['weekday'] == 'Monday':
            monday_found = True
            week_count += 1
            week_group.append(week_count)
        else:
            week_group.append(week_count)

    week_df['week_group'] = week_group

    # Group and include min/max dates for range
    week_df = week_df.groupby('week_group').agg({
        'date': ['min', 'max'],
        'calories': 'mean',
        'weight': 'mean',
        'bmr': 'mean'
    }).reset_index()

    # Flatten multi-level columns
    week_df.columns = ['week_group', 'week_start', 'week_end', 'calories', 'weight', 'bmr']

    # Round values
    week_df['calories'] = week_df['calories'].round(0).astype(int)
    week_df['weight'] = week_df['weight'].round(1)

    # Optional: add a formatted date range column
    week_df['week_range'] = week_df['week_start'].dt.strftime('%b %d') + ' - ' + week_df['week_end'].dt.strftime('%b %d')
    week_df['x_name'] = week_df['week_group'].astype(str) + ' : ' + week_df['week_range']
    del week_df['week_start']
    del week_df['week_end']


    # weekly averages

    fig = go.Figure()

    # Plot Weight on primary y-axis
    fig.add_trace(go.Scatter(
        x=week_df['x_name'], 
        y=week_df['weight'],
        mode='lines+markers',
        name='Weight (lbs)',
        line=dict(color='blue'),
        yaxis='y1'
    ))

    # Plot Food Calories on secondary y-axis
    fig.add_trace(go.Scatter(
        x=week_df['x_name'], 
        y=week_df['calories'],
        mode='lines+markers',
        name='Calories',
        line=dict(color='green'),
        yaxis='y2'
    ))

    # BMR on secondary y-axis
    fig.add_trace(go.Scatter(
        x=week_df['x_name'], 
        y=week_df['bmr'],
        mode='lines',
        name='BMR',
        line=dict(color='red', dash='dash'),
        yaxis='y2'
    ))

    # Layout and axis formatting
    fig.update_layout(
        title='Weekly Weight AVG, Calorie Intake AVG, BMR AVG',
        xaxis=dict(title='Date'),
        yaxis=dict(
            title=dict(text='Weight (lbs)', font=dict(color='blue')),
            tickfont=dict(color='blue')
        ),
        yaxis2=dict(
            title=dict(text='Calories', font=dict(color='green')),
            tickfont=dict(color='green'),
            overlaying='y',
            side='right'
        ),
        legend=dict(x=0.5, y=1.15, orientation='h', xanchor='center'),
        margin=dict(t=80),
        hovermode='x unified',
        template='plotly_white'
    )


    # Optional: save to HTML file
    # fig.write_html("static/simple_week_avg_interactive_chart.html")

    graph_html = pio.to_html(fig, full_html=False)
    return graph_html


def calorie_weight_change(df):
    # ----- Processing -----
    df['weight_change']  = df['weight'].diff()
    df['caloric_balance'] = df['calories'] - df['bmr']
    df_clean = df.dropna()

    # ----- Plotly scatter plot -----
    fig = px.scatter(
        df_clean,
        x='caloric_balance',
        y='weight_change',
        hover_data=['date', 'calories', 'bmr', 'weight'],
        title='Caloric Balance vs. Daily Weight Change',
        labels={
            'caloric_balance': 'Caloric Balance (Calories - BMR)',
            'weight_change': 'Weight Change (lbs)'
        }
    )

    # Reference lines at x=0 & y=0
    fig.add_shape(type="line", x0=0, x1=0,
                  y0=df_clean['weight_change'].min(), y1=df_clean['weight_change'].max(),
                  line=dict(color="gray", dash="dash"))
    fig.add_shape(type="line", y0=0, y1=0,
                  x0=df_clean['caloric_balance'].min(), x1=df_clean['caloric_balance'].max(),
                  line=dict(color="gray", dash="dash"))

    fig.update_layout(template="plotly_white")

    # Export to HTML string
    graph_html = fig.to_html(full_html=False, include_plotlyjs='cdn')   # or pio.to_html(...)
    return graph_html


def calories_vs_weight(df):
    print(df.head())
    # Ensure 'date' column is datetime for tooltip formatting
    df['date'] = pd.to_datetime(df['date'])

    # Plotly scatter plot
    fig = px.scatter(
        df,
        x='calories',
        y='weight',
        hover_data=['date', 'bmr'],
        title='Calories vs. Weight',
        labels={
            'calories': 'Calories Consumed',
            'weight': 'Weight (lbs)'
        }
    )

    fig.update_layout(template="plotly_white")

    # Return HTML string to embed
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def calories_distribution(df, bin_size=100):
    fig = px.histogram(
        df,
        x='calories',
        nbins=int((df['calories'].max() - df['calories'].min()) / bin_size),
        title='Distribution of Daily Calorie Intake',
        labels={'calories': 'Calories Consumed'},
        color_discrete_sequence=['blue']
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title='Calories',
        yaxis_title='Frequency (Days)'
    )

    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def forecast_weight(df, target_date=None):
    if target_date is None:
        target_date = datetime.now().date() + timedelta(days=30)

    df = df.sort_values(by='date')  # Ensure DataFrame is sorted by date
    dates = df['date'].tolist()  # Use dates from the DataFrame

    # Convert datetime objects to numerical format (days since start)
    start_date = min(dates)
    x_numeric = [(date - start_date).days for date in dates]
    y = df['weight'].tolist()  # Use weight data from the DataFrame

    # Perform linear regression
    slope, intercept, r, p, std_err = stats.linregress(x_numeric, y)

    def myfunc(x):
        return slope * x + intercept

    mymodel = [myfunc(x) for x in x_numeric]

    target_numeric_date = (target_date - start_date).days
    predicted_weight = round(myfunc(target_numeric_date),1)

    # Generate forecasted dates up to target_date
    forecast_dates = [start_date + pd.Timedelta(days=i) for i in range(max(x_numeric), target_numeric_date + 1)]
    forecast_weights = [myfunc(i) for i in range(max(x_numeric), target_numeric_date + 1)]

    # Create interactive plot with Plotly
    fig = go.Figure()

    # Scatter plot for weight data
    fig.add_trace(go.Scatter(x=dates, y=y, mode='lines+markers', name='Weight (lbs)', line=dict(color='blue')))

    # Line plot for regression line
    fig.add_trace(go.Scatter(x=dates, y=mymodel, mode='lines', name='Model Line', line=dict(color='gray')))

    # Forecasted green line up to target_date
    fig.add_trace(go.Scatter(x=forecast_dates, y=forecast_weights, mode='lines+markers', name='Forecasted Weight', line=dict(color='green')))

    # Customize layout
    fig.update_layout(title="Weight Over Time",
                    xaxis_title="Date",
                    yaxis_title="Weight",
                    xaxis=dict(tickformat="%Y-%m-%d"),
                    legend=dict(x=0.5, y=1.15, orientation='h', xanchor='center'),
                    margin=dict(t=80),
                    hovermode='x unified',
                    template='plotly_white')

    return fig.to_html(full_html=False, include_plotlyjs='cdn'), target_date.strftime('%m-%d-%Y'), predicted_weight

