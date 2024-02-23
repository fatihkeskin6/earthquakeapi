import threading
import time
import pandas as pd
import streamlit as st
from get_data import get_data as gd
from to_db import to_db as td
import schedule

todb = td()

def etl_in_every_5():
    todb.write_to_db()

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

def main():

    st.title('My Streamlit App')


    minutes_left, seconds_left = calculate_time_left()
    st.write(f"Time left: {minutes_left} minutes {seconds_left} seconds")
    schedule.every(1).minutes.do(etl_in_every_5)
    print('s')
    # Start the scheduler loop in a separate thread
    threading.Thread(target=schedule_thread, daemon=True).start()

    if st.button('Display Graphic'):
        df = get_recent_data()
        st.line_chart(df[['date', 'mw']])

if __name__ == '__main__':
        # Schedule the ETL function to run every 1 minute
    main()
