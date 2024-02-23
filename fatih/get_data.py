import re
import json
import pandas as pd
from urllib.request import urlopen
from datetime import datetime
from bs4 import BeautifulSoup
class get_data():
    @staticmethod
    def get_from_api():
        try:
            array = []
            data = urlopen('http://www.koeri.boun.edu.tr/scripts/sondepremler.asp').read()
            soup = BeautifulSoup(data, 'html.parser')
            data = soup.find_all('pre')
            data = str(data).strip().split('--------------')[2]

            data = data.split('\n')
            data.pop(0)
            data.pop()
            data.pop()
            for index in range(len(data)):
                element = str(data[index].rstrip())
                element = re.sub(r'\s\s\s', ' ', element)
                element = re.sub(r'\s\s\s\s', ' ', element)
                element = re.sub(r'\s\s', ' ', element)
                element = re.sub(r'\s\s', ' ', element)
                Args = element.split(' ')
                location = Args[8]+element.split(Args[8])[len(element.split(
                    Args[8])) - 1].split('İlksel')[0].split('REVIZE')[0]
                json_data = json.dumps({
                    "id": index+1,
                    "date": Args[0]+" "+Args[1],
                    "timestamp": int(datetime.strptime(Args[0]+" "+Args[1], "%Y.%m.%d %H:%M:%S").timestamp()),
                    "latitude": float(Args[2]),
                    "longitude": float(Args[3]),
                    "depth": float(Args[4]),
                    "size": {
                        "md": float(Args[5].replace('-.-', '0')),
                        "ml": float(Args[6].replace('-.-', '0')),
                        "mw": float(Args[7].replace('-.-', '0'))
                    },
                    "location": location.strip(),
                    "attribute": element.split(location)[1].split()[0]
                }, sort_keys=False)

                array.append(json.loads(json_data))
                df = pd.DataFrame(array)
                df = df.drop(columns=['timestamp'])
                # Assuming 'size' is the name of the column containing the dictionary
                df['md'] = df['size'].apply(lambda x: x['md'])
                df['ml'] = df['size'].apply(lambda x: x['ml'])
                df['mw'] = df['size'].apply(lambda x: x['mw'])

                # Now you can drop the 'size' column if you no longer need it
                df = df.drop(columns=['size'])
            return df
        except:
            return []