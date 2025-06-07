import pandas as pd
import plotly.graph_objects as go
import numpy as np

def advanced_chart(df):
    # advanced chart

    fig = go.Figure()

    # Plot Weight on primary y-axis
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['Weight'],
        mode='lines+markers',
        name='Weight (lbs)',
        line=dict(color='blue'),
        yaxis='y1'
    ))

    # Weight trend line
    x_numeric = df['Str_Date'].map(pd.Timestamp.toordinal)
    z = np.polyfit(x_numeric, df['Weight'], 1)
    p = np.poly1d(z)
    fig.add_trace(go.Scatter(
        x=df['Date'], y=p(x_numeric),
        mode='lines',
        name='Weight Trend',
        line=dict(color='blue', dash='dash'),
        yaxis='y1'
    ))

    # Plot Food Calories on secondary y-axis
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['Food Calories'],
        mode='lines+markers',
        name='Calories',
        line=dict(color='green'),
        yaxis='y2'
    ))

    # Calorie trend line
    z = np.polyfit(x_numeric, df['Food Calories'], 1)
    p = np.poly1d(z)
    fig.add_trace(go.Scatter(
        x=df['Date'], y=p(x_numeric),
        mode='lines',
        name='Calorie Trend',
        line=dict(color='green', dash='dash'),
        yaxis='y2'
    ))

    # BMR on secondary y-axis
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['BMR'],
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
    fig.write_html("static/advanced_interactive_chart.html")

def simple_chart(df):
    # simple chart

    fig = go.Figure()

    # Plot Weight on primary y-axis
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['Weight'],
        mode='lines+markers',
        name='Weight (lbs)',
        line=dict(color='blue'),
        yaxis='y1'
    ))

    # Plot Food Calories on secondary y-axis
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['Food Calories'],
        mode='lines+markers',
        name='Calories',
        line=dict(color='green'),
        yaxis='y2'
    ))

    # BMR on secondary y-axis
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['BMR'],
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
    fig.write_html("static/simple_interactive_chart.html")

def avg_chart(df):
    week_df = df.copy()
    week_df['Date'] = pd.to_datetime(week_df['Date'])  # Ensure Date is datetime
    week_df['Weekday'] = week_df['Date'].dt.day_name()

    monday_found = False
    week_count = 0
    week_group = []

    for index, row in week_df.iterrows():
        if (row['Weekday'] != 'Monday' and monday_found == False):
            week_group.append(week_count)
        elif row['Weekday'] == 'Monday':
            monday_found = True
            week_count += 1
            week_group.append(week_count)
        else:
            week_group.append(week_count)

    week_df['Week_group'] = week_group

    # Group and include min/max dates for range
    week_df = week_df.groupby('Week_group').agg({
        'Date': ['min', 'max'],
        'Food Calories': 'mean',
        'Weight': 'mean',
        'BMR': 'mean'
    }).reset_index()

    # Flatten multi-level columns
    week_df.columns = ['Week_group', 'Week_Start', 'Week_End', 'Food Calories', 'Weight', 'BMR']

    # Round values
    week_df['Food Calories'] = week_df['Food Calories'].round(0).astype(int)
    week_df['Weight'] = week_df['Weight'].round(1)

    # Optional: add a formatted date range column
    week_df['Week_Range'] = week_df['Week_Start'].dt.strftime('%b %d') + ' - ' + week_df['Week_End'].dt.strftime('%b %d')
    week_df['x_name'] = week_df['Week_group'].astype(str) + ' : ' + week_df['Week_Range']
    del week_df['Week_Start']
    del week_df['Week_End']


    # weekly averages

    fig = go.Figure()

    # Plot Weight on primary y-axis
    fig.add_trace(go.Scatter(
        x=week_df['x_name'], y=week_df['Weight'],
        mode='lines+markers',
        name='Weight (lbs)',
        line=dict(color='blue'),
        yaxis='y1'
    ))

    # Plot Food Calories on secondary y-axis
    fig.add_trace(go.Scatter(
        x=week_df['x_name'], y=week_df['Food Calories'],
        mode='lines+markers',
        name='Calories',
        line=dict(color='green'),
        yaxis='y2'
    ))

    # BMR on secondary y-axis
    fig.add_trace(go.Scatter(
        x=week_df['x_name'], y=week_df['BMR'],
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
    fig.write_html("static/simple_week_avg_interactive_chart.html")
