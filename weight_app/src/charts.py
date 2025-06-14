import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np

def daily_chart(df):
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

def daily_trend_chart(df):
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
