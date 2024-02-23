import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import pyodbc

# Veritabanından verileri almak için bir fonksiyon
def get_latest_earthquakes():
    # Veritabanından son 10 depremi al
    server = 'clicq-db.database.windows.net'
    database = 'dbd3c'
    username = 'clicq-dev'
    password = '1441Fatih'
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

    query = "SELECT TOP 10 Tarih, Saat, Derinlik, Yer, Enlem, Boylam FROM Beyza.EarthquakeData ORDER BY Tarih DESC, Saat DESC"
    earthquake_data = pd.read_sql(query, conn)

    conn.close()

    return earthquake_data

# Streamlit uygulaması
def main():
    st.title('Son 10 Deprem Görselleştirme')

    # Veritabanından son 10 depremi al
    latest_earthquakes = get_latest_earthquakes()

    # Harita oluştur
    m = folium.Map(location=[39.9334, 32.8597], zoom_start=6)
    st.write(m)

    # Son 10 depremin her birini haritaya ekle
    for idx, earthquake in latest_earthquakes.iterrows():
        folium.Marker(
            location=[earthquake['Enlem'], earthquake['Boylam']],
            popup=f"{earthquake['Tarih']} {earthquake['Saat']}",
            icon=folium.Icon(color='red' if earthquake['Derinlik'] > 5 else 'blue')
        ).add_to(m)

    # Haritayı görüntüle
    st.write(m)
    folium_static(m)

if __name__ == "__main__":
    main()
