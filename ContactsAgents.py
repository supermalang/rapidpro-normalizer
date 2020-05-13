#%% 
## Extraction des données
import http.client
import mimetypes
import json
conn = http.client.HTTPSConnection("api.rapidpro.io")
payload = ''
headers = {
  'Authorization': 'Token 50cbd586af288261b69996ef9aaf0a43fb6351a9'
}
conn.request("GET", "/api/v2/contacts.json?flow=bb56ec73-0246-42e1-bc0b-632a6f2a4d81", payload, headers)
res = conn.getresponse()
data = res.read()

import requests
#from dotenv import load_dotenv
import pandas as pd
import numpy as np
import calendar
from datetime import date
from datetime import datetime
import time

#%%
## Exploitation des données
data_contacts_agents = json.loads(data)
data_contacts_agents = data_contacts_agents.get("results")

#%%
## Transformation des données
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

### Temps moyen de rapportage de l'agent dans l'année
#moyenne(delai d'envoi de rapports) && annee_en_cours 
Delai_rapport = pd.DataFrame(columns=['Delai_rapport_Janvier','Delai_rapport_Fevrier','Delai_rapport_Mars','Delai_rapport_Avril','Delai_rapport_Mai','Delai_rapport_Juin','Delai_rapport_Juillet','Delai_rapport_Aout','Delai_rapport_Septembre','Delai_rapport_Octobre','Delai_rapport_Novembre','Delai_rapport_Decembre'], dtype='int')

if maintenant.month == 2 :
     Delai_rapport['Delai_rapport_Janvier'] = Delai_envoi_rapport_mensuel  
if maintenant.month == 3 :
     Delai_rapport['Delai_rapport_Fevrier'] = Delai_envoi_rapport_mensuel
if maintenant.month == 4 :
     Delai_rapport['Delai_rapport_Mars'] = Delai_envoi_rapport_mensuel
if maintenant.month == 5 :
     Delai_rapport['Delai_rapport_Avril'] = Delai_envoi_rapport_mensuel
if maintenant.month == 6 :
     Delai_rapport['Delai_rapport_Mai'] = Delai_envoi_rapport_mensuel
if  maintenant.month == 7 :
     Delai_rapport['Delai_rapport_Juin'] = Delai_envoi_rapport_mensuel
if  maintenant.month == 8 :
     Delai_rapport['Delai_rapport_Juillet'] = Delai_envoi_rapport_mensuel
if  maintenant.month == 9 :
     Delai_rapport['Delai_rapport_Aout'] = Delai_envoi_rapport_mensuel
if  maintenant.month == 10 :
     Delai_rapport['Delai_rapport_Septembre'] = Delai_envoi_rapport_mensuel
if maintenant.month == 11 :
     Delai_rapport['Delai_rapport_Octobre'] = Delai_envoi_rapport_mensuel
if  maintenant.month == 12 :
     Delai_rapport['Delai_rapport_Novembre'] = Delai_envoi_rapport_mensuel
if  maintenant.month == 1 :
     Delai_rapport['Delai_rapport_Decembre'] = Delai_envoi_rapport_mensuel       

Delai_rapport=Delai_rapport.replace(r'', np.NaN)

def time_to_date(tab_delai_mensuel, k):
    Temps_moyen_rapportage=[]
    for a in range(len(tab_delai_mensuel)):
        i=3
        somme_delai=0
        while i <= (k-2):
                somme_delai = somme_delai +tab_delai_mensuel.iloc[a,i] 
                i= i+1
        Temps_moyen_rapportage.append(somme_delai / (k - 4)) 
    return Temps_moyen_rapportage

Temps_moyen_rapportage = time_to_date(Delai_rapport,maintenant.month)
data_contacts_agents['Temps_moyen_rapportage']= Temps_moyen_rapportage

### Temps moyen d'envoi de rapport de rappels  dans l'annee
##moyenne(delai d'envoi de rapport de rappel) && annee_en_cours
Delai_rapport_rappel = pd.DataFrame(columns=['Delai_rapport_rappel_Janvier','Delai_rapport_rappel_Fevrier','Delai_rapport_rappel_Mars','Delai_rapport_rappel_Avril','Delai_rapport_rappel_Mai','Delai_rapport_rappel_Juin','Delai_rapport_rappel_Juillet','Delai_rapport_rappel_Aout','Delai_rapport_rappel_Septembre','Delai_rapport_rappel_Octobre','Delai_rapport_rappel_Novembre','Delai_rapport_rappel_Decembre'], dtype='int')

if maintenant.month == 2 :
     Delai_rapport_rappel['Delai_rapport_rappel_Janvier'] = Delai_envoi_rapport_rappel_mensuel  
if maintenant.month == 3 :
     Delai_rapport_rappel['Delai_rapport_rappel_Fevrier'] = Delai_envoi_rapport_rappel_mensuel
if maintenant.month == 4 :
     Delai_rapport_rappel['Delai_rapport_rappel_Mars'] = Delai_envoi_rapport_rappel_mensuel
if maintenant.month == 5 :
     Delai_rapport_rappel['Delai_rapport_rappel_Avril'] = Delai_envoi_rapport_rappel_mensuel
if maintenant.month == 6 :
     Delai_rapport_rappel['Delai_rapport_rappel_Mai'] = Delai_envoi_rapport_rappel_mensuel
if  maintenant.month == 7 :
     Delai_rapport_rappel['Delai_rapport_rappel_Juin'] = Delai_envoi_rapport_rappel_mensuel
if  maintenant.month == 8 :
     Delai_rapport_rappel['Delai_rapport_rappel_Juillet'] = Delai_envoi_rapport_rappel_mensuel
if  maintenant.month == 9 :
     Delai_rapport_rappel['Delai_rapport_rappel_Aout'] = Delai_envoi_rapport_rappel_mensuel
if  maintenant.month == 10 :
     Delai_rapport_rappel['Delai_rapport_rappel_Septembre'] = Delai_envoi_rapport_rappel_mensuel
if maintenant.month == 11 :
     Delai_rapport_rappel['Delai_rapport_rappel_Octobre'] = Delai_envoi_rapport_rappel_mensuel
if  maintenant.month == 12 :
     Delai_rapport_rappel['Delai_rapport_rappel_Novembre'] = Delai_envoi_rapport_rappel_mensuel
if  maintenant.month == 1 :
     Delai_rapport_rappel['Delai_rapport_rappel_Decembre'] = Delai_envoi_rapport_rappel_mensuel

Delai_rapport_rappel=Delai_rapport_rappel.replace(r'', np.NaN)

Temps_moyen_rapportage_rappel = time_to_date(Delai_rapport_rappel,maintenant.month)
data_contacts_agents['Temps_moyen_rapportage_rappel']= Temps_moyen_rapportage_rappel

### Nombre de rapport délivré par chaque agent
#### somme des rapports + somme des rapports de rappel 
Nombre_rapport =pd.DataFrame(columns=['Nombre_rapport_Janvier', 'Nombre_rapport_Fevrier', 'Nombre_rapport_Mars', 'Nombre_rapport_Avril', 'Nombre_rapport_Mai', 'Nombre_rapport_Juin', 'Nombre_rapport_Juillet','Nombre_rapport_Aout','Nombre_rapport_Septembre', 'Nombre_rapport_Octobre', 'Nombre_rapport_Novembre', 'Nombre_rapport_Decembre'], dtype='int')
somme_rapport_mensuel= data_contacts_agents['Nombre_rapport_mensuel'] + data_contacts_agents['Nombre_rapport_de_rappel_mensuel']

if maintenant.month == 2 :
     Nombre_rapport['Nombre_rapport_Janvier'] = somme_rapport_mensuel
if maintenant.month == 3 :
     Nombre_rapport['Nombre_rapport_Fevrier'] = somme_rapport_mensuel
if maintenant.month == 4 :
     Nombre_rapport['Nombre_rapport_Mars'] = somme_rapport_mensuel
if maintenant.month == 5 :
     Nombre_rapport['Nombre_rapport_Avril'] = somme_rapport_mensuel
if maintenant.month == 6 :
       Nombre_rapport['Nombre_rapport_Mai'] = somme_rapport_mensuel
if  maintenant.month == 7 :
      Nombre_rapport['Nombre_rapport_Juin'] = somme_rapport_mensuel
if  maintenant.month == 8 :
      Nombre_rapport['Nombre_rapport_Juillet'] = somme_rapport_mensuel
if  maintenant.month == 9 :
      Nombre_rapport['Nombre_rapport_Aout'] = somme_rapport_mensuel
if  maintenant.month == 10 :
      Nombre_rapport['Nombre_rapport_Septembre'] = somme_rapport_mensuel
if maintenant.month == 11 :
     Nombre_rapport['Nombre_rapport_Octobre'] = somme_rapport_mensuel
if  maintenant.month == 12 :
      Nombre_rapport['Nombre_rapport_Novembre'] = somme_rapport_mensuel
if  maintenant.month == 1 :
      Nombre_rapport['Nombre_rapport_Decembre'] = somme_rapport_mensuel

### 
def nombre_rapports_delivres(tab_rapport_mensuel, k):
    Nombre_rapports_delivres=[]
    for a in range(len(tab_rapport_mensuel)):
        i=3
        total_rapport=0
        while i <= (k-2):
                total_rapport = total_rapport + tab_rapport_mensuel.iloc[a,i] 
                i= i+1
        Nombre_rapports_delivres.append(total_rapport) 
    return Nombre_rapports_delivres

Nombre_rapports_delivres= nombre_rapports_delivres(Nombre_rapport, maintenant.month)
data_contacts_agents['Nombre_rapports_delivres']= Nombre_rapports_delivres

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

filename= 'data_contacts_agents.csv'
data_contacts_agents.to_csv(filename, index=False, header=True, encoding='iso-8859-1')
