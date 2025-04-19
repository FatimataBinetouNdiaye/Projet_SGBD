import subprocess
import os

def retrain_ai_model(professor_feedback):
    """
    Fonction pour réentraîner le modèle IA basé sur le feedback du professeur.
    Ici, on sauvegarde le feedback dans un fichier et on appelle un script local pour réentraîner le modèle.
    """
    # Enregistrer le feedback dans un fichier texte
    feedback_file_path = os.path.join("feedback_data", "feedback_data.txt")
    
    # Crée le dossier "feedback_data" si il n'existe pas déjà
    if not os.path.exists("feedback_data"):
        os.makedirs("feedback_data")
    
    with open(feedback_file_path, "a") as f:
        f.write(professor_feedback + "\n")

    # Logique d'entraînement de l'IA ici : appel à un script Python pour réentraîner le modèle
    print(f"Feedback reçu pour réentraîner le modèle : {professor_feedback}")

    # Appel à un script local qui s'occupera de réentraîner le modèle en utilisant le fichier de feedback
    try:
        subprocess.run(["python3", "scripts/train_model.py", "--feedback_file", feedback_file_path], check=True)
        print("Réentraînement du modèle terminé avec succès.")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors du réentraînement du modèle : {e}")
