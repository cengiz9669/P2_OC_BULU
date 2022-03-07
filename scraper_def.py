from typing import Any, Dict, List

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

def recuperation_informations_page_livre(url_page_livre) -> Dict[str, str]:
    '''Fonction permettant d'extraire les informations d'un livre dans une liste en sortie à partir de son url.'''

    # Initialisation requête + data
    response = requests.get(url_page_livre)
    response.encoding = response.apparent_encoding

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
        data['product_page_url'] = url_page_livre

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
        data['product_description'] = blocks_texte[3].text

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


def telechargement_image_livre(image_url_value, upc_value):
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


def ecriture_csv(categorie_livre, liste_donnees_par_livre: List[Dict[str, str]]):
    '''Fonction pour créer le fichier CSV pour une catégorie donnée.
    Le fichier portera le nom de la catégorie entrée en argument.'''

    headers_csv = [
        'product_page_url',
        'universal_product_code',
        'title',
        'price_including_tax',
        'price_excluding_tax',
        'number_available',
        'product_description',
        'category',
        'review_rating',
        'image_url',
    ]

    # Création Dossier 'Donnees_Resultat' si nécessaire dans le répertoire de travail
    if os.path.exists(repertoire_de_travail + '/Donnees_Resultat') == False:
        os.makedirs(repertoire_de_travail + '/Donnees_Resultat')

    # Création du CSV portant le nom de la catégorie et écriture des entêtes
    nom_du_csv = repertoire_de_travail + '/Donnees_Resultat/' + str(categorie_livre) + '.csv'
    print(f'Ecriture du csv {nom_du_csv}')

    with open(nom_du_csv, 'w', newline='', encoding="utf8") as csvfile:
        writer = csv.DictWriter(csvfile, delimiter = ";", fieldnames=headers_csv)
        writer.writeheader()
        writer.writerows(liste_donnees_par_livre)

    print(f'{len(liste_donnees_par_livre)} livres écrits pour la catégorie {categorie_livre}.')


def extraire_liste_livres(categorie_livre_url) -> List[str]:
    '''Fonction permettant d'obtenir en sortie une liste contenant l'url de chacun des livres présents dans la catégorie.
    Cette fonction est récursive pour tenir compte de la pagination.'''

    # Initialisation requête
    response = requests.get(categorie_livre_url)
    response.encoding = response.apparent_encoding

    # Récupération des informations
    if response.ok:

        # HTML PARSER
        soup = BeautifulSoup(response.text, 'html.parser')

        # Recherche des url de livres
        blocks_livres = soup.find_all('li', class_='col-xs-6 col-sm-4 col-md-3 col-lg-3')
        donnees_liste_livre = []
        for livre in blocks_livres:
            donnees_liste_livre.append(str('http://books.toscrape.com/catalogue/'+ str(livre).split('"')[7].split('../../../')[1]))

        # Detection page 'Next' et itération
        block_url_page_suivante = soup.find_all('li', class_='next')
        if block_url_page_suivante != []:
            url_livre_base = ''
            url_livre_base_liste = categorie_livre_url.split('/')[:-1]
            for element in url_livre_base_liste:
                url_livre_base += str(element) + '/'
            donnees_liste_livre += extraire_liste_livres(
                url_livre_base + str(block_url_page_suivante[0]).split('"')[3]
            )

        return donnees_liste_livre


def ecriture_categorie(categorie_livre_url):
    '''Fonction permettant d'extraire toutes les informations de tous les livres d'une même catégorie.
    Toutes ces informations seront écrites sur un même fichier CSV portant le nom de la categorie'''

    # Extraire liste des url de livres
    liste_livre = extraire_liste_livres(categorie_livre_url)

    # Initialisation CSV par catégorie
    categorie: str = recuperation_informations_page_livre(liste_livre[0])['category']

    # Itération sur tous les livres dans la catégorie
    donnees_par_livre = []
    for livre in liste_livre:
        donnees_par_livre.append(recuperation_informations_page_livre(livre))

    ecriture_csv(categorie, donnees_par_livre)


def extraire_list_categorie_url_extraction(contenu_html) -> List[str]:
    # HTML PARSER
    soup = BeautifulSoup(contenu_html, 'html.parser')
    liste_categorie = []

    # Block Liste de categorie
    block_categories = soup.find('ul', class_='nav nav-list')
    block_categories_lignes = block_categories.find_all('a')

    # Itération sur chaque categorie
    for categorie in range(1, len(block_categories_lignes)):
        liste_categorie.append(
            str(
                'https://books.toscrape.com/catalogue/category/'
                + str(block_categories_lignes[categorie])
                .split('"')[1]
                .split('../')[1]
            )
        )
    return liste_categorie
    

def extraire_liste_categorie_url() -> List[str]:
    '''Fonction permettant d'extraire dans une liste l'ensemble des categories disponibles sous forme d'url.'''

    # Initialisation requête + liste_categorie
    response = requests.get(books_home_url)
    response.encoding = response.apparent_encoding
    
    # Récupération des informations
    if response.ok:
        categories = extraire_list_categorie_url_extraction(response.text)
        return categories


def extraire_tout():
    '''Fonction permettant d'extraire les informations de tous les produits parmis toutes les catégories du site'''

    # Extraction de la liste des catégories
    print(f"Début de l'extraction des catégories")
    liste_categorie = extraire_liste_categorie_url()
    print(f"{len(liste_categorie)} catégories extraites")
    print('------ Traitement par catégorie ------')

    # Extraction des informations de tous les livres pour chaque catégorie
    for categorie_url in liste_categorie:
        print(f"Traitement de la catégorie {categorie_url}")
        ecriture_categorie(categorie_url)
        print('------------')


extraire_tout()
