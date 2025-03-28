from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def detecter_plagiat(texte1, texte2):
    vecteur = TfidfVectorizer().fit_transform([texte1, texte2])
    score_similarite = cosine_similarity(vecteur[0], vecteur[1])
    return score_similarite[0][0]
