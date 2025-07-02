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
top500_data={}
for link in links[4:99]:
    if link.text.strip().startswith('June') or  link.text.strip().startswith('November'):
        print("Scraping " + str(link.text.strip()))
        conn = http.client.HTTPSConnection("www.top500.org")
        conn.request("GET", str(link['href']))
        top500_list = conn.getresponse()
        content = top500_list.read()
        soup2 = BeautifulSoup(content, 'html.parser')
        conn.close()
        soup2.prettify()
        table = soup2.find('table', class_='table-condensed')
        rows = table.find_all('tr')[1:]
        top500_data[link.text.strip()] = []
        for row in rows[:3]:
            cols = row.find_all('td')
            entry = {
                    'Rank': int(''.join(cols[0].text.strip().split(','))),
                    'System': ' '.join(cols[1].stripped_strings),
                    'Cores': int(''.join(cols[2].text.strip().split(','))),
                    'Rmax (TFlop/s)': normalize_flops(parse_number(''.join(cols[3].text.strip().split(','))), link.text.strip()),
                    'Rpeak (TFlop/s)': normalize_flops(parse_number(''.join(cols[4].text.strip().split(','))), link.text.strip()),
                    'Power (kW)': parse_number(''.join(cols[5].text.strip().split(','))),
                }
            top500_data[link.text.strip()].append(entry)
connection.close()
years = []
performance = []
for datestr in sorted(top500_data.keys(), key = lambda x: datetime.strptime(x, '%B %Y')):
    top1 = top500_data[datestr][0]
    rmax = top1.get('Rmax (TFlop/s)')
    if rmax:
        years.append(datetime.strptime(datestr, '%B %Y'))
        performance.append(rmax)

plt.figure(figsize=(12, 6))
plt.plot(years, performance, marker='o', linestyle='-', color='blue', label='Top 1 Rmax (PFlop/s)')

plt.title('Performanta calculatoarelor in timp')
plt.xlabel('An')
plt.ylabel('Rmax (TFlop/s)')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.legend()
plt.show()

