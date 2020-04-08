#%% [markdown]
## Assignements
#Les données utilisées dans ce fichier sont extraites de l'API **GET /api/v2/contacts.json** dans RapidPro.
#Elles sont récupérées par le client Postman.
#Et à partir de Postman on importe les données sur jupyter.

#Ce travail s'intéresse sur la remise des rapports de naissances des agents.

# %%
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
print(data.decode("utf-8"))

#%% [markdown]
## Exploitation des données

#%%
type(data)

#%% [markdown]
### Conversion en dictionnaire

#%%
data_contacts_agents = json.loads(data)
type(data_contacts_agents)


# %% [markdown]
### Extraction des informations de la clé 'results' de notre dictionnaire 'data_contacts_agents'

#%%
data_contacts_agents = data_contacts_agents.get("results")
type(data_contacts_agents)

# %% [markdown]
#### Un exemple de la structure de notre liste 'data_contacts_agents'

#%%
data_contacts_agents[2]

# %% [markdown]
## Transformation des données

#%% [markdown]
### Extension de chaque dictionnaire de la liste data_contacts_agents par les colonnes suivantes :

#- Extraction des valeurs de la clé 'groups' : 'name'(pour extraire la Région)

#- Extraction des valeurs de la clé 'fields' : 'departement', 'commune', 'date_enregistrement', 'date_rapport_agent', 'compteur_retard_rapport_agent_ec', 'date_rapport_de_rappel', 'reporting_month', 'date_rapport', 'mois_de_rapport', 'mois_dernier_rapport', 'ec', 'annee_en_cours',
#'date_completude_du_rapport', 'mois_de_rappel'

# %%
for a in  range(len(data_contacts_agents)):
    #Extraction des valeurs du champs 'groups'
    if not data_contacts_agents[a]['groups']:
        break
    else :
        Region = data_contacts_agents[a]['groups'][0]['name']    
    Departement = data_contacts_agents[a]['fields'].get('departement')
    Commune = data_contacts_agents[a]['fields'].get('commune')
    date_enregistrement = data_contacts_agents[a]['fields'].get('date_enregistrement')
    date_rapport_agent = data_contacts_agents[a]['fields'].get('date_rapport_agent')   
    compteur_retard_rapport_agent_ec= data_contacts_agents[a]['fields'].get('compteur_retard_rapport_agent_ec')
    date_rapport_de_rappel = data_contacts_agents[a]['fields'].get('date_rapport_de_rappel')
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
                                    'date_enregistrement' : date_enregistrement,
                                    'date_rapport_agent' : date_rapport_agent,
                                    'compteur_retard_rapport_agent_ec' : compteur_retard_rapport_agent_ec,
                                    'date_rapport_de_rappel' : date_rapport_de_rappel,
                                    'reporting_month' : reporting_month,
                                    'date_rapport' : date_rapport,
                                    'mois_de_rapport' : mois_de_rapport,
                                    'mois_dernier_rapport' : mois_dernier_rapport,
                                    'ec' : ec,
                                    'annee_en_cours' : annee_en_cours,
                                    'date_completude_du_rapport' : date_completude_du_rapport,
                                    'mois_de_rappel' : mois_de_rappel})



# %% [markdown]
### Conversion de la liste 'data_contacts_agents' en dataFrame

# %%
import pandas as pd
data_contacts_agents = pd.DataFrame(data_contacts_agents)
data_contacts_agents

# %% [markdown]
### Division de la colonne 'created_on' en deux colonnes différentes :
#- 'create_on_date'
#- 'create_on_heure'

# %%
data_contacts_agents=data_contacts_agents.join(data_contacts_agents['created_on'].str.split('T', 1, expand=True).rename(columns={0:'created_on_date', 1:'created_on_heure'}))

# %% [markdown]
#### Conversion de la colonne 'created_on_date' au format datatime

#%%
data_contacts_agents.created_on_date= pd.to_datetime(data_contacts_agents.created_on_date) 

# %% [markdown]
#### Creation des colonnes: 'created_on_year', 'created_on_month', 'created_on_day'

#%%
data_contacts_agents['created_on_year'] = data_contacts_agents['created_on_date'].dt.year
data_contacts_agents['created_on_month'] = data_contacts_agents['created_on_date'].dt.month
data_contacts_agents['created_on_day'] = data_contacts_agents['created_on_date'].dt.day

# %% [markdown]
### Suppression des colonnes qu'on ne vas pas utiliser

#%%
data_contacts_agents=data_contacts_agents.drop(['uuid','language', 'groups', 'fields',], axis=1)

# %% [markdown]
### Affichage des colonnes restantes et de la taille du DataFrame 'data_contacts_agents'
print(data_contacts_agents.columns)

# %% [markdown]
### Le type de données de chaque colonne du DataFrame 

# %%
data_contacts_agents.info()

# %% [markdown]
### Le nombre de valeurs manquantes pour chaque variable du DataFrame 'data_contacts_agents'

# %%
data_contacts_agents.isna().sum()

