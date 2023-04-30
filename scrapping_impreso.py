import requests
from bs4 import BeautifulSoup
from collections import Counter
from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')

from pymongo import MongoClient

# conexion con la base de datos
conexion = "mongodb://localhost:27017/"
cliente = MongoClient(conexion)

# Selecciona la base de datos que quiere guardar 
db = cliente['motor']
collection = db['palabras']


# pagina donde se hara el webscrapping
url = 'https://scrapy.org/'

# manda un request al html
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# encuentra todos los link por que vienen en una etiqueta <a>
links = soup.find_all('a')

# define una funcion que recolectar el website y extrae las palabras mas buscadas 
def recolector(url):
    try:
        # mande un requeste al html y saca el contenido 
        response = requests.get(url)
        if response.content is None:
            raise ValueError('No content found')
        soup = BeautifulSoup(response.content, 'html.parser')

        # encuentra el texto de la pagina
        texto = soup.get_text()

        # separa las palabras 
        palabras = texto.split()

        # elimina las stopwords
        stop_words = set(stopwords.words('english'))
        palabras = [palabra for palabra in palabras if palabra.lower() not in stop_words]

        # cuenta las palabras que hay
        cont_palabras = Counter(palabras)

        # selecionas las tres palabras mas buscadas, enumera en una lista las tres palabras mas comunes y las ordena por rank y las agrega ala lista de palbras comunes 
        comun_palabras = [(palabra, cont, rank+1) for rank, (palabra, cont) in enumerate(cont_palabras.most_common(3))]

        return comun_palabras
    except ValueError:
        print(f"Error: No content found for {url}")
        return None
    except Exception as e:
        print(f"Error scraping website {url}: {e}")
        return None
    
# Define una funcion y guarda los resultados en la base de datos
def guarda_db(result):
    if result is not None:
        collection.insert_one(result)
        print(f"Saved to MongoDB: {result}")
        # imprime las palabras y el rank
        palabras = result['palabras']
        print(f"palabras on {result['url']}:") 
        for palabra, cont, rank in palabras:
            print(f"{rank}. {palabra}: {cont}")

# creat un hijo de 10 com trabajadores
with ThreadPoolExecutor(max_workers=10) as executor:
    
    #interior de cada link y lo busca
    for link in links:
        href = link.get('href')
        if href is None or href.strip() == '':
            continue
        if not href.startswith('http://') and not href.startswith('https://'):
            continue
        future = executor.submit(recolector, href)
        def guarda_resultado_db(future):
            result = future.result()
            guarda_db({"url": href, "palabras": result})
        future.add_done_callback(guarda_resultado_db)