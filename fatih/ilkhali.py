import re
import json
import pandas as pd
from urllib.request import urlopen
from datetime import datetime
from bs4 import BeautifulSoup
from flask import Flask, render_template

app = Flask(__name__)

def getKandilliData():
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
        return array
    except:
        return []

@app.route('/')
def index():
    data = getKandilliData()
    df = pd.DataFrame(data)
    return render_template('index.html', tables=[df.to_html(classes='data')], titles=df.columns.values)

if __name__ == '__main__':
    app.run(debug=True)
