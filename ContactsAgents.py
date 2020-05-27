
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import http.client
import mimetypes
import json
import requests
import pandas as pd
import numpy as np
import calendar
from datetime import date
from datetime import datetime
import time


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


conn = http.client.HTTPSConnection("api.rapidpro.io")
payload = ''
TOKEN = os.getenv("TOKEN")

headers = { 'Authorization': 'Token ' + TOKEN }
conn.request("GET", "/api/v2/contacts.json?flow=bb56ec73-0246-42e1-bc0b-632a6f2a4d81", payload, headers)
res = conn.getresponse()
data = res.read()

data_contacts_agents = json.loads(data)
data_contacts_agents = data_contacts_agents.get("results")

for a in  range(len(data_contacts_agents)):
    #Extraction des valeurs du champs 'groups'
    if not data_contacts_agents[a]['groups']:
        continue
    else :
        Region = data_contacts_agents[a]['groups'][0]['name']
        #Departement = data_contacts_agents[a]['groups'][1]['name']
        #Commune = data_contacts_agents[a]['groups'][2]['name']
        
    Departement = data_contacts_agents[a]['fields'].get('departement')
    Commune = data_contacts_agents[a]['fields'].get('commune')   
    compteur_retard_rapport_agent_ec= data_contacts_agents[a]['fields'].get('compteur_retard_rapport_agent_ec')
    date_rapport_de_rappel = data_contacts_agents[a]['fields'].get('date_rapport_de_rappel')
    rappels_de_rapport = data_contacts_agents[a]['fields'].get('rappels_de_rapport')
    reporting_month = data_contacts_agents[a]['fields'].get('reporting_month')
    date_rapport = data_contacts_agents[a]['fields'].get('date_rapport')
    mois_de_rapport = data_contacts_agents[a]['fields'].get('mois_de_rapport')
    mois_dernier_rapport = data_contacts_agents[a]['fields'].get('mois_dernier_rapport')
    ec = data_contacts_agents[a]['fields'].get('ec')
    annee_en_cours = data_contacts_agents[a]['fields'].get('annee_en_cours')
    date_completude_du_rapport = data_contacts_agents[a]['fields'].get('date_completude_du_rapport')
    mois_de_rappel = data_contacts_agents[a]['fields'].get('mois_de_rappel')
    data_contacts_agents[a].update({'Region': Region,
                                    'Departement' : Departement,
                                    'Commune': Commune,
                                    'compteur_retard_rapport_agent_ec' : compteur_retard_rapport_agent_ec,
                                    'date_rapport_de_rappel' : date_rapport_de_rappel,
                                    'rappels_de_rapport' : rappels_de_rapport,
                                    'reporting_month' : reporting_month,
                                    'date_rapport' : date_rapport,
                                    'mois_de_rapport' : mois_de_rapport,
                                    'mois_dernier_rapport' : mois_dernier_rapport,
                                    'ec' : ec,
                                    'annee_en_cours' : annee_en_cours,
                                    'date_completude_du_rapport' : date_completude_du_rapport,
                                    'mois_de_rappel' : mois_de_rappel})

### Conversion de la liste 'data_contacts_agents' en dataFrame
data_contacts_agents = pd.DataFrame(data_contacts_agents)

### les colonnes qu'il faut supprimer
data_contacts_agents=data_contacts_agents.drop(['language', 'groups', 'fields','blocked','stopped','modified_on','reporting_month','date_completude_du_rapport',], axis=1)

### Filtrage du DataFrame par la région de Kolda
data_contacts_agents = data_contacts_agents.loc[data_contacts_agents['Region']=="REGION: Kolda"]

### Conversion du type des colonnes du Dataframe 
data_contacts_agents=data_contacts_agents.astype({
    "name" : str,  "Region" : str,"Departement" : str, "Commune" : str, "mois_de_rapport" : str,
    "mois_dernier_rapport": str, "ec" :str, "mois_de_rappel" : str, "urns" : str,
    "rappels_de_rapport" : int})

data_contacts_agents['annee_en_cours'].fillna(0, inplace=True)
data_contacts_agents['annee_en_cours'] = data_contacts_agents['annee_en_cours'].astype(int)
data_contacts_agents = data_contacts_agents.loc[data_contacts_agents['annee_en_cours']!=0]

#filtrage des agents qui ont deux numéros
longueur_tel = data_contacts_agents.urns.str.len()
data_contacts_agents = data_contacts_agents.loc[longueur_tel==21]

### Réindexation du dataframe
data_contacts_agents = data_contacts_agents.reset_index(drop=True)

### Conversion des colonnes définissant des dates au format datatime
data_contacts_agents.created_on = pd.to_datetime(data_contacts_agents.created_on)  
data_contacts_agents.date_rapport_de_rappel=  pd.to_datetime(data_contacts_agents.date_rapport_de_rappel)
data_contacts_agents.date_rapport = pd.to_datetime(data_contacts_agents.date_rapport)

### Extraction du jour, mois et de l'année des variables suivantes
date_rapport_month = data_contacts_agents['date_rapport'].dt.month
date_rapport_de_rappel_month = data_contacts_agents['date_rapport_de_rappel'].dt.month
date_rapport_de_rappel_year = data_contacts_agents['date_rapport_de_rappel'].dt.year
date_rapport_day = data_contacts_agents['date_rapport'].dt.day

month_rapport =data_contacts_agents['mois_de_rapport']
maintenant = datetime.now()

### Enumération des mois de l'année
mois_en_nombre= {'Janvier' : 1, 'Fevrier' : 2, 'Mars' : 3, 'Avril' : 4, 'Mai' : 5, 'Juin' : 6,
                 'Juillet' : 7, 'Aout': 8, 'Septembre' : 9, 'Octobre' : 10, 'Novembre' : 11,
                 'Decembre' : 12}

### Définition de la fonction qui donne l'équivalent des mois en nombre
def Mois_en_nombre(col_mois):
    Mois_enumere= []
    for el in col_mois:
        if el in mois_en_nombre :
            k = mois_en_nombre.get(el)
        else :
            k = 0
        Mois_enumere.append(k)
    return Mois_enumere

### Définition de la fonction qui donne le type de rapportage mensuel
def type_rapportage_mensuel(x,y):
    Type_rapportage = []
    for a in range(len(data_contacts_agents)):
        if (x[a] - y[a]) == 1 and  (date_rapport_day[a] <= 10):
            Type_rapportage.append('rapport')
        elif (x[a] - y[a]) == 1 and (date_rapport_day[a] >= 10)  and  (date_rapport_day[a] <= 31):
            Type_rapportage.append('retard')
        else :
            Type_rapportage.append('rappel')
    return Type_rapportage

### Ajout de la colonne 'Type_rapportage_mensuel' au Dataframe
Type_rapportage_mensuel = type_rapportage_mensuel(date_rapport_month,Mois_en_nombre(month_rapport))
data_contacts_agents['Type_rapportage_mensuel'] = Type_rapportage_mensuel

### Nombre de rapport mensuel par agent
def nombre_rapport(x,y):
    Nombre_rapport = []
    for a in range(len(data_contacts_agents)):
        if (x[a] - y[a]) == 1 :
            Nombre_rapport.append(1)
        else :
            Nombre_rapport.append(0)
    return Nombre_rapport

Nombre_rapport_mensuel = nombre_rapport(date_rapport_month,Mois_en_nombre(month_rapport))
data_contacts_agents['Nombre_rapport_mensuel'] = Nombre_rapport_mensuel

### Nombre de rapport de rappel mensuel par agent
def nombre_rapport_de_rappel(x,y):
    Nombre_rapport_de_rappel = []
    annee_en_cours= data_contacts_agents['annee_en_cours']
    for a in range(len(data_contacts_agents)):
        if (x[a] - y[a]) != 1 and  (date_rapport_de_rappel_year[a] == annee_en_cours[a]):
            Nombre_rapport_de_rappel.append(1)
        else :
            Nombre_rapport_de_rappel.append(0)
    return Nombre_rapport_de_rappel

Nombre_rapport_de_rappel_mensuel = nombre_rapport_de_rappel(date_rapport_de_rappel_month,Mois_en_nombre(month_rapport))
data_contacts_agents['Nombre_rapport_de_rappel_mensuel'] = Nombre_rapport_de_rappel_mensuel

### Nombre de notifications d'envoi de rapport par mois par agent
#C'est équivalent à la valeur de la variable rappels_de_rapport.

### Délai d'envoi de rapports à temps
#### date_rapport - 1er jour succédant le mois_de_rapport
def delai_envoi_rapport(x,y):
    Delai_envoi_rapport = []
    for a in range(len(data_contacts_agents)):
        if data_contacts_agents['annee_en_cours'][a]== 0 :
            Delai_envoi_rapport.append('')
        else :
            first_delai = date(data_contacts_agents['annee_en_cours'][a], Mois_en_nombre(y)[a] + 1, 1)
            k = (x.dt.date[a] - first_delai).days 
            Delai_envoi_rapport.append(k)
    return Delai_envoi_rapport

Delai_envoi_rapport_mensuel = delai_envoi_rapport(data_contacts_agents['date_rapport'],data_contacts_agents['mois_de_rapport'])
data_contacts_agents['Delai_envoi_rapport_mensuel'] = Delai_envoi_rapport_mensuel
data_contacts_agents['Delai_envoi_rapport_mensuel'] = data_contacts_agents['Delai_envoi_rapport_mensuel'].astype(int, errors= 'ignore')

### Delai d'envoi de rapport de rappel
#### date_rapport_de_rappel - 10eme jour succédant le mois_de_rappel
def delai_envoi_rapport_rappel(x,y):
    Delai_envoi_rapport_rappel = []
    for a in range(len(data_contacts_agents)):
        if data_contacts_agents['annee_en_cours'][a]== 0 or date_rapport_de_rappel_year[a] != data_contacts_agents['annee_en_cours'][a]:
            Delai_envoi_rapport_rappel.append('')
        else :
            first_delai = date(data_contacts_agents['annee_en_cours'][a], Mois_en_nombre(y)[a] + 1, 10)
            k = (x.dt.date[a] - first_delai).days 
            Delai_envoi_rapport_rappel.append(k)
    return Delai_envoi_rapport_rappel

Delai_envoi_rapport_rappel_mensuel = delai_envoi_rapport_rappel(data_contacts_agents['date_rapport_de_rappel'],data_contacts_agents['mois_de_rappel'])
data_contacts_agents['Delai_envoi_rapport_rappel_mensuel'] = Delai_envoi_rapport_rappel_mensuel
data_contacts_agents['Delai_envoi_rapport_rappel_mensuel'] = data_contacts_agents['Delai_envoi_rapport_rappel_mensuel'].astype(int, errors= 'ignore')


### Nombre de rapport délivré par chaque agent
#### somme des rapports + somme des rapports de rappel 
Nombre_rapports_delivres= data_contacts_agents['Nombre_rapport_mensuel'] + data_contacts_agents['Nombre_rapport_de_rappel_mensuel']
data_contacts_agents['Nombre_rapports_delivres']= Nombre_rapports_delivres
data_contacts_agents['Nombre_rapports_delivres']=data_contacts_agents['Nombre_rapports_delivres'].astype(int)

######## Quelques corrections sur les colonnes du dataframe 

######## Quelques corrections sur les colonnes du dataframe 

### Unification des mots comme Vélingara
data_contacts_agents['Departement'] = data_contacts_agents['Departement'].str.replace('Velingara','Vélingara')

### Remplacer 'Decembre annee precedente' par 'Decembre' 
data_contacts_agents[['mois_de_rapport','mois_dernier_rapport']] = data_contacts_agents[['mois_de_rapport','mois_dernier_rapport']].replace('Decembre annee precedente','Decembre')

### Enlever les crochets de urns
data_contacts_agents['urns'] = data_contacts_agents['urns'].str[6:19]
data_contacts_agents['urns']=data_contacts_agents['urns'].astype(str)

### Enlever le mot "REGION: " de Region 
data_contacts_agents['Region'] = data_contacts_agents['Region'].str[8:]

data_contacts_agents_rapport= data_contacts_agents[['uuid', 'name', 'urns', 'created_on', 'Region', 'Departement',
       'Commune', 'compteur_retard_rapport_agent_ec',
       'rappels_de_rapport', 'date_rapport', 'mois_de_rapport',
       'mois_dernier_rapport', 'annee_en_cours', 'mois_de_rappel',
       'Type_rapportage_mensuel', 'Nombre_rapport_mensuel', 'Delai_envoi_rapport_mensuel','Nombre_rapports_delivres']]

data_contacts_agents_rappel= data_contacts_agents[['uuid', 'name', 'urns', 'created_on', 'Region', 'Departement',
       'Commune', 'compteur_retard_rapport_agent_ec', 'date_rapport_de_rappel',
       'rappels_de_rapport', 'mois_de_rapport',
       'mois_dernier_rapport', 'annee_en_cours', 'mois_de_rappel',
       'Type_rapportage_mensuel', 'Nombre_rapport_de_rappel_mensuel',
       'Delai_envoi_rapport_rappel_mensuel', 'Nombre_rapports_delivres']]

#Ajout de l'horodatage aux noms de fichiers à exporter : DateExportFichier et Heure
suffixe=  maintenant.strftime('%Y-%m-%d') + '_' + maintenant.strftime('%H-%M-%S') 
filename_rapport= 'data_contacts_agents_rapport_' + suffixe + '.csv'
filename_rappel= 'data_contacts_agents_rappel_' + suffixe + '.csv'

#Exportation des fichiers en csv
data_contacts_agents_rapport.to_csv(filename_rapport, index=False, header=True, encoding='iso-8859-1')
data_contacts_agents_rappel.to_csv(filename_rappel, index=False, header=True, encoding='iso-8859-1')

