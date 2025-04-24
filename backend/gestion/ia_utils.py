from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from gestion.models import Soumission

llm = Ollama(model="deepseek-coder:6.7b")

def corriger_soumission_avec_ia(soumission: Soumission):
    # Lire le contenu texte du PDF
    texte_soumis = soumission.extraire_texte_pdf()

    # Récupérer l'énoncé de l’exercice lié
    enonce = soumission.exercice.texte_enonce

    prompt = PromptTemplate.from_template("""
Tu es un correcteur automatique intégré à une plateforme IA. Tu dois évaluer une copie d'étudiant répondant à un exercice SQL.

Réponds uniquement en JSON dans ce format exact :

{
  "note": "12/20",
  "feedback": "Très bon usage des jointures, mais certaines requêtes sont inefficaces.",
  "points_forts": "Requêtes correctement formulées, bonne compréhension des tables",
  "points_faibles": "Optimisation des requêtes manquante, erreurs dans la clause GROUP BY"
}

Voici l’énoncé de l’exercice :
{enonce}

Voici la copie de l’étudiant :
{reponse}

⚠️ Tu ne dois répondre que par le JSON. Ne donne aucun autre texte ou explication hors du JSON.
""")

    final_prompt = prompt.format(enonce=enonce, reponse=texte_soumis)
    result = llm.invoke(final_prompt)

    import json
    try:
        return json.loads(result)
    except Exception as e:
        print("Erreur de parsing JSON depuis la réponse IA :", result)
        return None
