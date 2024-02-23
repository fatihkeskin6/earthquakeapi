from flask import Flask, render_template
import pyodbc
import pandas as pd
import plotly.express as px
import requests
import schedule
import time
from threading import Thread

app = Flask(__name__)
 
# Veritabanı bağlantısı
conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                      'Server=clicq-db.database.windows.net;'
                      'Database=dbd3c;'
                      'UID=Simgeren;'
                      'PWD=37Simere;')
cursor = conn.cursor()
server = 'clicq-db.database.windows.net'
database = 'dbd3c'
username = 'Simgeren'
password = '37Simere'
driver = '{ODBC Driver 17 for SQL Server}'
 
        
connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
connection = pyodbc.connect(connection_string)
# Veritabanından veri çekme fonksiyonu
def get_data():
    query = """SELECT title, date, magnitude FROM deprem ORDER BY date desc"""
    df = pd.read_sql(query,connection)
    df['date'] = pd.to_datetime(df['date'])
 
    print(df)
   
    return df
 
# Flask route
@app.route('/')
def index():
    data = get_data()  
 
    # Create a bar chart 
    fig = px.bar(data, x='date', y='magnitude', title='Earthquake Magnitude Over Time',
                 labels={'date': 'Date', 'magnitude': 'Magnitude'},  # Labels for axes
                 hover_data={'date': '|%B %d, %Y %I:%M:%S %p', 'magnitude': ':.2f', 'title': True},  # Custom hover data
                 template='plotly', height=500)
    fig.update_xaxes(type='category')
 
    print(fig)
 
    # Convert the Plotly figure to HTML 
    plot_html = fig.to_html(full_html=False)
 
    return render_template('index_plotly.html', plot_html=plot_html)
def fetch_and_insert_data():
    try:
        url = "https://api.orhanaydogdu.com.tr/deprem/kandilli/live"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            formatted_data = []

            for record in data["result"]:
                earthquake_id = record['earthquake_id']
                cursor.execute('SELECT 1 FROM deprem WHERE earthquake_id = ?', earthquake_id)
                existing_record = cursor.fetchone()

                if not existing_record:
                   
                    formatted_record = {
                        'earthquake_id': earthquake_id,
                        'provider': record['provider'],
                        'title': record['title'],
                        'date': record['date'],
                        'magnitude': record['mag'],
                        'depth': record['depth'],
                        'latitude': record['geojson']['coordinates'][1],
                        'longitude': record['geojson']['coordinates'][0],
                        'closest_city_name': record['location_properties']['closestCity']['name'],
                        'closest_city_code': record['location_properties']['closestCity']['cityCode'],
                        'closest_city_distance': record['location_properties']['closestCity']['distance'],
                        'closest_city_population': record['location_properties']['closestCity']['population'],
                        'epi_center_name': record['location_properties']['epiCenter']['name'],
                        'epi_center_code': record['location_properties']['epiCenter']['cityCode'],
                        'epi_center_population': record['location_properties']['epiCenter']['population']
                    }

                    cursor.execute('''
                         INSERT INTO deprem          
                        (earthquake_id, provider, title, date, magnitude, depth, latitude, longitude,
                         closest_city_name, closest_city_code, closest_city_distance, closest_city_population,
                         epi_center_name, epi_center_code, epi_center_population)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        formatted_record['earthquake_id'],
                        formatted_record['provider'],
                        formatted_record['title'],
                        formatted_record['date'],
                        formatted_record['magnitude'],
                        formatted_record['depth'],
                        formatted_record['latitude'],
                        formatted_record['longitude'],
                        formatted_record['closest_city_name'],
                        formatted_record['closest_city_code'],
                        formatted_record['closest_city_distance'],
                        formatted_record['closest_city_population'],
                        formatted_record['epi_center_name'],
                        formatted_record['epi_center_code'],
                        formatted_record['epi_center_population']
                    ))

                    conn.commit()
                    print(f"Yeni veri eklendi: {formatted_record['title']}")
                else:
                    print(f"Veri zaten mevcut: {record['title']}")

            print("Veri çekildi ve veritabanına eklendi.")
        else:
            print("API çağrısı başarısız. HTTP status code:", response.status_code)

    except Exception as e:
        print(f"Bir hata oluştu: {e}")
if __name__ == '__main__':
    # Schedule the fetch_and_insert_data function to run every 1 minute
    schedule.every(1).minutes.do(fetch_and_insert_data)

    # Run the Flask app and the scheduler in the main thread
    flask_thread = Thread(target=app.run, kwargs={'debug': True, 'use_reloader': False})
    flask_thread.start()

    while True:
        # Bir sonraki çalışma zamanını hesapla
        time_left = schedule.idle_seconds()
        print(f"Next run in {time_left:.2f} seconds")
        schedule.run_pending()
        time.sleep(1)