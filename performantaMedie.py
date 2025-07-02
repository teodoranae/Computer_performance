from datetime import datetime
import http.client
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

def parse_number(value):
    try:
        return float(value.replace(',', ''))
    except ValueError:
        return None

def normalize_flops(value, date_string):
    dt = datetime.strptime(date_string, '%B %Y')
    if dt < datetime(2005, 6, 1):
        return value / 1_000_000
    elif dt < datetime(2019, 6, 1):
        return value / 1_000
    else:
        return value

connection = http.client.HTTPSConnection("www.top500.org")
connection.request("GET", "/")
response = connection.getresponse()
html_doc = response.read()
soup = BeautifulSoup(html_doc, 'html.parser')
dropdown = soup.find('li', {'id': '13'})
links = soup.find_all('a', href = True)
month_avg = {}
for link in links[4:99]:
    if link.text.strip().startswith('June') or  link.text.strip().startswith('November'):
        print("Processing " + str(link.text.strip()))
        conn = http.client.HTTPSConnection("www.top500.org")
        conn.request("GET", str(link['href']))
        top500_list = conn.getresponse()
        content = top500_list.read()
        soup2 = BeautifulSoup(content, 'html.parser')
        conn.close()
        soup2.prettify()
        table = soup2.find('table', class_='table-condensed')
        rows = table.find_all('tr')[1:]
        month_avg[link.text.strip()] = 0
        ct = 0
        for row in rows:
            cols = row.find_all('td')
            month_avg[link.text.strip()] +=normalize_flops(parse_number(''.join(cols[3].text.strip().split(','))), link.text.strip())
            ct+=1
        month_avg[link.text.strip()] /= ct
connection.close()

yearly_avg = {}
for month, val in month_avg.items():
    dt = datetime.strptime(month, '%B %Y')
    if dt.year not in yearly_avg.keys():
        yearly_avg[dt.year] = []

    yearly_avg[dt.year].append(val)

yearly_avg = {year: sum(vals) / len(vals) for year, vals in yearly_avg.items()}
years = []
yearly_performance = []
for year in sorted(yearly_avg.keys(), key = lambda x: x):
    years.append(year)
    yearly_performance.append(yearly_avg[year])

plt.figure(figsize=(12, 6))
plt.plot(years, yearly_performance, marker='o', linestyle='-', color='blue', label='medie')

plt.title('Performanta calculatoarelor in timp')
plt.xlabel('An')
plt.ylabel('Performanta medie (PFlop/s)')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.legend()
plt.show()



