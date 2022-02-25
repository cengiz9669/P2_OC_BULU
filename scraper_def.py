from typing import Any, Dict, List
from time import time

import requests
from bs4 import BeautifulSoup
import csv
import os

# Constantes
repertoire_de_travail = str(os.path.dirname(os.path.realpath(__file__)))
books_home_url = 'https://books.toscrape.com/catalogue/category/books_1/index.html'
review_ratings_values = {
    'One': '1',
    'Two': '2',
    'Three': '3',
    'Four': '4',
    'Five': '5',
}

def recuperation_informations_page_livre(url_page_livre: str) -> Dict[str, str]:
    '''Fonction permettant d'extraire les informations d'un livre dans une liste en sortie à partir de son url.'''

    # Initialisation requête + data
    response = requests.get(url_page_livre)


    data = {
        'product_page_url': '',
        'universal_product_code': '',
        'title': '',
        'price_including_tax': '',
        'price_excluding_tax': '',
        'number_available': '',
        'product_description': '',
        'category': '',
        'review_rating': '',
        'image_url': '',
    }

    # Récupération des informations
    if response.ok:
        # URL de la page produit ('product_page_url')
        data['product_page_url'] = str(url_page_livre)

        # HTML PARSER
        soup = BeautifulSoup(response.text, 'html.parser')

        # Titre du livre ('title')
        block_titre = soup.find_all('div', class_='col-sm-6 product_main')
        data['title'] = str(block_titre[0].find('h1').text)


        # Récupération du block 'Product Information'
        elements =[]
        elements = soup.find_all("td")
        price_including_tax = elements[3].text[1:]
        price_excluding_tax = elements[2].text[1:]
        number_available_string = elements[5].text
        number_available_string_list = number_available_string.split()
        number_string = number_available_string_list[2].replace("(", "")
        number = int(number_string)
        upc = elements[0].string

        data ['price_including_tax'] = price_including_tax
        data ['price_excluding_tax'] = price_excluding_tax
        data ['number_available'] = number
        data ['universal_product_code'] = upc

        # Description Produit ('product_description')
        blocks_texte = soup.find_all('p')
        data['product_description'] = str(blocks_texte[3].text)

        # Catégorie ('category')
        block_categories = soup.find('ul', class_='breadcrumb')
        data['category'] = str(block_categories.find_all('li')[2].find('a').text)

        # URL de l'image ('image_url')
        block_image = soup.find('div', class_='item active').find('img')
        data['image_url'] = 'http://books.toscrape.com/' + block_image['src']

       # Récupération image de couverture
        telechargement_image_livre(data['image_url'], data['universal_product_code'])
        

        # Avis ('review_rating')
        review_rating = soup.find(class_="star-rating")
        notation = review_rating["class"][1]
        data['review_rating'] = review_ratings_values.get(notation)
        
        return data


def telechargement_image_livre(image_url_value: str, upc_value: str):
    '''Fonction permettant de télécharger l'image de couverture du livre correspondant à l'url du livre en entrée.
    Toutes les images de couvertures seront placées dans le dossier '/Donnees_Resultat/Couvertures' présent dans le dossier de travail.
    Toutes les images de couvertures seront nommées par la valeur de l'UPC.'''


# Création Dossier 'Couvertures' si nécessaire dans le dossier 'Donnees_Resultat'
    if os.path.exists(repertoire_de_travail + '/Donnees_Resultat' + '/Couvertures') == False:
        os.makedirs(repertoire_de_travail + '/Donnees_Resultat' + '/Couvertures')

    # Enregistrement de l'image de couverture
    r = requests.get(image_url_value, allow_redirects=True)
    image_path = repertoire_de_travail + '/Donnees_Resultat' + '/Couvertures' + '/' + upc_value + '.jpeg'
    open(image_path, 'wb').write(r.content)

