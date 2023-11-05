import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import time
import sqlite3
import matplotlib.pyplot as plt

url = "https://www.macrotrends.net/stocks/charts/TSLA/tesla/revenue"

# Configura encabezados personalizados para simular una solicitud de navegador
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}

response = requests.get(url, headers=headers)
time.sleep(10)
if response.status_code == 200:
    # Paso 3: Transforma el HTML
    soup = bs(response.text, "html.parser")


# 1. Buscar todas las tablas.
# 2. Encontrar la tabla con la evolución trimestral.
revenues = soup.find_all('table', class_="historical_data_table")[1] # Seleciono la segunda tabla, donde están los datos trimestrales

df = pd.DataFrame(columns = ["Date", "Revenue"])
list1 = []
list2 = []

rows = revenues.find_all('tr')
for row in rows:
    cols = row.find_all('td')
    if len(cols) == 0:
        continue
    else:
        list1.append(cols[0].text)
        list2.append(cols[1].text)

# 3. Almacena los datos en un DataFrame.
df = pd.DataFrame({'Date': list1, 'Revenue': list2})
# df.head(10)

# Limpia las filas eliminando "$", comas y celdas vacías o sin info
def clean_data(value):
    if isinstance(value, str):
        value = value.replace('$', '').replace(',', '') 
        value = value.strip() 
        if value == '':
            return None  # Convierte a None si el valor está vacío
        else:
            return value
    else:
        return value

# Aplica la función de limpieza a las columnas 'Date' y 'Revenue'
df['Date'] = df['Date'].apply(clean_data)
df['Revenue'] = df['Revenue'].apply(clean_data)

# Elimina filas con valores nulos o vacíos
df = df.dropna()
# df.head(10)


# 1. Crea la tabla.
# 2. Inserta los valores.
# 3. Almacena (``commit`) los cambios.

con = sqlite3.connect('tesla_revenue.db')
cursor = con.cursor()

create_table_query = '''
CREATE TABLE IF NOT EXISTS Tesla_quaterly_revenue (
    id INTEGER PRIMARY KEY,
    Date TEXT,
    Revenue REAL
);
'''
cursor.execute(create_table_query)

for index, row in df.iterrows():
    date = row['Date']
    revenue = row['Revenue']
    insert_query = 'INSERT INTO Tesla_quaterly_revenue (Date, Revenue) VALUES (?, ?);'
    cursor.execute(insert_query, (date, revenue))

con.commit()

con.close()

# ¿Qué tipos de visualizaciones podemos realizar?
# Propón al menos 3 y muéstralos.

# GRÁFICO DE BARRAS:

plt.figure(figsize=(10, 6))
plt.bar(df['Date'], df['Revenue'])
plt.xlabel('Fecha')
plt.ylabel('Ingresos')
plt.title('Ingresos Trimestrales de Tesla')
plt.xticks(rotation=45)  # Rota las etiquetas del eje x para una mejor legibilidad
plt.show()


# GRÁFICO DE LÍNEAS:

plt.figure(figsize=(10, 6))
plt.plot(df['Date'], df['Revenue'], marker='o', linestyle='-', color='b')
plt.xlabel('Fecha')
plt.ylabel('Ingresos')
plt.title('Tendencia de Ingresos Trimestrales de Tesla')
plt.xticks(rotation=45)
plt.grid(True)
plt.show()


# GRÁFICO DE DISPERSIÓN:

plt.figure(figsize=(10, 6))
plt.scatter(df['Date'], df['Revenue'], color='g', marker='o')
plt.xlabel('Fecha')
plt.ylabel('Ingresos')
plt.title('Gráfico de Dispersión')
plt.xticks(rotation=45)
plt.show()
