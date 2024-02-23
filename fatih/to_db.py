import pandas as pd
from get_data import get_data as gd
import pyodbc

class to_db():

    @staticmethod
    def initial():
        server = 'clicq-db.database.windows.net'
        database = 'dbd3c'
        username = 'clicq-dev'
        password = '1441Fatih'
        driver = '{ODBC Driver 17 for SQL Server}'

        # Create a connection string
        connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"

        # Create a connection
        connection = pyodbc.connect(connection_string)
        get_data = gd()
        df = get_data.get_from_api()
        df.drop('id', axis=1, inplace=True)
        df = df.iloc[::-1].reset_index(drop=True)
        df['etl_date'] = pd.to_datetime('now')
        connection = pyodbc.connect(connection_string)

        # Create a cursor
        cursor = connection.cursor()

        for index, row in df.iterrows():
            insert_query = """
            INSERT INTO EarthquakeData (date, latitude, longitude, depth, location, attribute, md, ml, mw, etl_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            values = (row['date'], row['latitude'], row['longitude'], row['depth'],
                        row['location'], row['attribute'], row['md'], row['ml'], row['mw'], row['etl_date'])
            cursor.execute(insert_query, values)

        # Commit the transaction
        connection.commit()

        # Close the cursor and connection
        cursor.close()
        connection.close()
        print('DATA IS REFRESHED')
    @staticmethod
    def write_to_db():
        # Database connection parameters
        server = 'clicq-db.database.windows.net'
        database = 'dbd3c'
        username = 'clicq-dev'
        password = '1441Fatih'
        driver = '{ODBC Driver 17 for SQL Server}'

        # Create a connection string
        connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"

        # Create a connection
        connection = pyodbc.connect(connection_string)

        # Query to select all rows from the table
        query = "SELECT * FROM EarthquakeData"

        # Read the table into a DataFrame
        old_df = pd.read_sql(query, connection)
        old_df = old_df.tail(50)
        # Close the connection
        connection.close()

        # Get new data from API
        get_data = gd()
        df = get_data.get_from_api()
        df.drop('id', axis=1, inplace=True)
        df = df.iloc[::-1].reset_index(drop=True)
        df['etl_date'] = pd.to_datetime('now')

        # Convert 'date' column in df to Timestamp
        df['date'] = pd.to_datetime(df['date'])

        # Assuming `old_df` is your existing DataFrame
        last_row = old_df.iloc[-1]  # Get the last row of old_df as a condition

        # Filter the new data based on the condition
        new_data = df[df['date'] > pd.to_datetime(last_row['date'])]

        if len(new_data) > 0:
            # Create a connection
            connection = pyodbc.connect(connection_string)

            # Create a cursor
            cursor = connection.cursor()

            for index, row in new_data.iterrows():
                insert_query = """
                INSERT INTO EarthquakeData (date, latitude, longitude, depth, location, attribute, md, ml, mw, etl_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                values = (row['date'], row['latitude'], row['longitude'], row['depth'],
                          row['location'], row['attribute'], row['md'], row['ml'], row['mw'], row['etl_date'])
                cursor.execute(insert_query, values)

            # Commit the transaction
            connection.commit()

            # Close the cursor and connection
            cursor.close()
            connection.close()
            print('DATA IS REFRESHED')
            return True
        else:
            print("No new data to insert.")
            return False
    @staticmethod
    def get_latest():
            # Database connection parameters
            server = 'clicq-db.database.windows.net'
            database = 'dbd3c'
            username = 'clicq-dev'
            password = '1441Fatih'
            driver = '{ODBC Driver 17 for SQL Server}'

            # Create a connection string
            connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"

            # Create a connection
            connection = pyodbc.connect(connection_string)

            # Query to select all rows from the table
            query = "SELECT TOP 100 * FROM EarthquakeData ORDER BY id DESC;"
            df = pd.read_sql(query,connection)
            return df