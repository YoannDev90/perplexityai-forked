from perplexity import Perplexity
from perplexity import mail


print("Démarrage du programme principal")
perplexity = Perplexity()
perplexity._login()
    
# Test de recherche
result = perplexity.search_sync("Bonjour, comment ça va ?")
print("Résultat de la recherche :", result)
    
perplexity.close()