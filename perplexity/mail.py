import requests
import json
import time
import string
import random
import re

def obtenir_domaine():
    domaines = requests.get("https://api.mail.tm/domains").json()["hydra:member"]
    domaine = domaines[0]["domain"]
    return domaine

def generer_adresse_email(domaine):
    caracteres = string.ascii_lowercase + string.digits
    randomseq = ''.join(random.choice(caracteres) for _ in range(8))
    adresse = f"{int(time.time())}-{randomseq}@{domaine}"
    mot_de_passe = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
    return adresse, mot_de_passe

def creer_compte_mailtm(adresse, mot_de_passe):
    compte = requests.post("https://api.mail.tm/accounts", json={
        "address": adresse,
        "password": mot_de_passe
    })
    if compte.status_code != 201:
        print(f"Erreur lors de la création du compte : {compte.text}")
        return None
    return compte

def obtenir_token(adresse, mot_de_passe):
    token_response = requests.post("https://api.mail.tm/token", json={
        "address": adresse,
        "password": mot_de_passe
    })
    if token_response.status_code != 200:
        print(f"Erreur lors de l'obtention du token : {token_response.text}")
        return None
    token = token_response.json()["token"]
    return token

def sauvegarder_infos_compte(adresse, mot_de_passe, token):
    infos_compte = {
        "adresse": adresse,
        "mot_de_passe": mot_de_passe,
        "token": token
    }
    with open("mail_tm_infos.json", "w") as f:
        json.dump(infos_compte, f, indent=4)

def lien_perplexity(token):
    headers = {"Authorization": f"Bearer {token}"}
    tentatives = 0
    print("Attente de l'email de Perplexity...")
    
    while tentatives < 60:  # Limite à 5 minutes d'attente
        messages_response = requests.get("https://api.mail.tm/messages", headers=headers)
        if messages_response.status_code != 200:
            print(f"Erreur lors de la récupération des messages : {messages_response.text}")
            return None
        
        messages = messages_response.json()["hydra:member"]
        print(f"Vérification des messages... ({tentatives + 1}/60)")
        
        for message in messages:
            print(f"Message reçu de : {message['from']['address']}")
            
            if message["from"]["address"] == "team@mail.perplexity.ai":
                contenu_response = requests.get(f"https://api.mail.tm/messages/{message['id']}", headers=headers)
                
                if contenu_response.status_code != 200:
                    print(f"Erreur lors de la récupération du contenu du message : {contenu_response.text}")
                    continue
                
                contenu = contenu_response.json()["text"]
                pattern = r'https://www\.perplexity\.ai/.*?token=[^&\s]+'
                match = re.search(pattern, contenu)
                
                if match:
                    print("Lien de connexion extrait avec succès")
                    return match.group(0)
        
        time.sleep(5)
        tentatives += 1
    
    print("Aucun email de Perplexity AI reçu après 5 minutes d'attente.")
    return None