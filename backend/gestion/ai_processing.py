import ollama

def corriger_exercice(texte_soumission, texte_correction):
    prompt = f"Compare la réponse suivante : {texte_soumission} avec la correction idéale : {texte_correction}. Donne une note sur 20 et un feedback."
    reponse = ollama.chat(model="deepseek", messages=[{"role": "user", "content": prompt}])
    return reponse['message']['content']
