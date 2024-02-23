import threading
import time
import pandas as pd
from flask import Flask, render_template,redirect, url_for
from get_data import get_data as gd
from to_db import to_db as td
import schedule
import plotly.express as px

app = Flask(__name__)

todb = td()

def etl_in_every_5():
    global df
    if todb.write_to_db():
        df = get_recent_data()

def get_recent_data():
    df = todb.get_latest()
    return df

def schedule_thread():
    while True:
        schedule.run_pending()
        time.sleep(1)

def calculate_time_left():
    next_run = schedule.next_run().timestamp()
    current_time = time.time()
    time_left = next_run - current_time
    minutes_left = int(time_left // 60)
    seconds_left = int(time_left % 60)
    return minutes_left, seconds_left

@app.route('/')
def index():
    get_data = gd()
    df = get_data.get_from_api()

    return render_template('index.html', tables=[df.to_html(classes='data')], titles=df.columns.values)

@app.route('/counter')
def graphic():
    return render_template('counter.html')

@app.route('/time-left')
def time_left():
    minutes_left, seconds_left = calculate_time_left()
    if minutes_left == 0 and seconds_left == 0:
        # If the time left is 0.0, redirect to the graphics page to refresh the page
        return redirect(url_for('graphics'))
    return {'minutes': minutes_left, 'seconds': seconds_left}

@app.route('/graphics')
def graphics():
    df = get_recent_data()  # Assuming this function retrieves the earthquake data
    fig = px.line(df, x='date', y='ml', title='Earthquake Magnitude Over Time', custom_data=['location'])
    fig.update_traces(mode='lines+markers', hovertemplate='date=%{x}<br>ml=%{y}<br>location=%{customdata[0]}')

    return render_template('graphics.html', plot=fig.to_html(include_plotlyjs='cdn'))

if __name__ == '__main__':
    # Schedule the ETL function to run every 1 minute
    schedule.every(10).minutes.do(etl_in_every_5)

    # Start the scheduler loop in a separate thread
    threading.Thread(target=schedule_thread, daemon=True).start()

    # Run the Flask app
    app.run(debug=True)
