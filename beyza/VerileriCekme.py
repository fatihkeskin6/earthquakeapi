import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import pyodbc

def main():
    # URL of the website to be scraped
    url = "http://www.koeri.boun.edu.tr/scripts/lst0.asp"
    response = requests.get(url)
    
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract text containing earthquake data
        text = soup.get_text()

        # Extract earthquake data
        earthquakes = re.findall(r'\d{4}\.\d{2}\.\d{2}\s+\d{2}:\d{2}:\d{2}\s+\d{2}\.\d+\s+\d{2}\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+(.+)', text)
        if not earthquakes:
            print("No earthquake data found on the page.")
            return

        # Initialize lists to store earthquake data
        dates = []
        times = []
        latitudes = []
        longitudes = []
        depths = []
        md_values = []
        ml_values = []
        mw_values = []
        locations = []

        # Iterate over each earthquake data and extract individual attributes
        for earthquake in earthquakes:
            data = earthquake.split()
            dates.append(data[0])
            times.append(data[1])
            latitudes.append(float(data[2]))
            longitudes.append(float(data[3]))
            depths.append(float(data[4]))
            md_values.append(float(data[6]))
            if data[7] == '-.-' or not data[7].replace('.', '').isdigit():
                ml_values.append(None)  # Sayısal olmayan veya "-.-" değeri varsa None olarak ekle
            else:
                ml_values.append(float(data[7]))
            if data[8] == '-.-' or not data[8].replace('.', '').isdigit():
                mw_values.append(None)  # Sayısal olmayan veya "-.-" değeri varsa None olarak ekle
            else:
                mw_values.append(float(data[8]))
            locations.append(' '.join(data[9:-1]))

        # Ensure all lists have the same length
        length = min(len(dates), len(times), len(latitudes), len(longitudes), len(depths), len(md_values), len(ml_values), len(mw_values), len(locations))

        # Create a DataFrame to hold the earthquake data
        earthquake_data = pd.DataFrame({
            'Date': dates[:length],
            'Time': times[:length],
            'Latitude': latitudes[:length],
            'Longitude': longitudes[:length],
            'Depth': depths[:length],
            'MD': md_values[:length],
            'ML': ml_values[:length],
            'Mw': mw_values[:length],
            'Location': locations[:length]
        })

        # Connect to MSSQL database
        server = 'clicq-db.database.windows.net'
        database = 'dbd3c'
        username = 'clicq-dev'
        password = '1441Fatih'
        conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

        # Write the earthquake data to MSSQL database table
        cursor = conn.cursor()
        for index, row in earthquake_data.iterrows():
            cursor.execute("INSERT INTO Beyza.EarthquakeData (Tarih, Saat, Enlem, Boylam, Derinlik, MD, ML, Mw, Yer) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   row['Date'], row['Time'], row['Latitude'], row['Longitude'], row['Depth'], row['MD'], row['ML'], row['Mw'], row['Location'])

        cursor.commit()
        cursor.close()
        conn.close()

    else:
        print("Error accessing the page. Status code:", response.status_code)

def get_latest_earthquakes():
    server = 'clicq-db.database.windows.net'
    database = 'dbd3c'
    username = 'clicq-dev'
    password = '1441Fatih'
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

    query = "SELECT TOP 10 Tarih, Saat, Derinlik, Yer, Enlem, Boylam FROM Beyza.EarthquakeData ORDER BY Tarih DESC, Saat DESC"
    earthquake_data = pd.read_sql(query, conn)

    conn.close()

    return earthquake_data

if __name__ == "__main__":
    main()
