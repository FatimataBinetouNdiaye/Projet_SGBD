import sqlparse

def check_sql_syntax(sql_query):
    """
    Vérifie la syntaxe d'une requête SQL.
    """
    try:
        # Utilisation de sqlparse pour analyser la requête
        parsed = sqlparse.parse(sql_query)
        if parsed:
            return True  # La requête est valide
    except Exception as e:
        return False  # Erreur de syntaxe
    return False

def generate_feedback(result, is_sql_valid):
    """
    Génère un feedback détaillé pour l'étudiant, en analysant les résultats de DeepSeek et
    en validant la syntaxe SQL.
    """
    feedback = {
        "feedback": "Solution correcte mais quelques erreurs mineures.",
        "points_forts": "Bonne utilisation des fonctions SQL.",
        "points_faibles": "La syntaxe de la requête SQL pourrait être améliorée.",
        "temps_execution": result.get("temps_execution", 0.0)
    }

    if not is_sql_valid:
        feedback["points_faibles"] = "Il y a une erreur de syntaxe dans la requête SQL. Veuillez revoir votre syntaxe."
    
    return feedback
