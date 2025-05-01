from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import fitz  # PyMuPDF
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator


from django.conf import settings
from django.core.files.base import ContentFile
from cryptography.fernet import Fernet
from io import BytesIO


#Début modification par diakhou
from django.contrib.auth.models import BaseUserManager

class UtilisateurManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, matricule, password=None, **extra_fields):
        """
        Crée et retourne un utilisateur avec un email, un mot de passe et les autres champs requis.
        """
        if not email:
            raise ValueError("L'email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, matricule=matricule, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, matricule, password=None, **extra_fields):
        """
        Crée et retourne un superutilisateur avec un mot de passe.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, first_name, last_name, matricule, password, **extra_fields)

#fin de la modification par Diakhou

class Utilisateur(AbstractUser):
    """
    Modèle personnalisé pour gérer tous les utilisateurs de la plateforme
    avec système de rôles (Étudiant/Professeur) et authentification OAuth
    """
   

    objects = UtilisateurManager()


    ETUDIANT = 'ET'
    PROFESSEUR = 'PR'
    ROLE_CHOICES = [
        (ETUDIANT, 'Étudiant'),
        (PROFESSEUR, 'Professeur'),
    ]

    # Champs de base
    role = models.CharField(max_length=2, choices=ROLE_CHOICES, verbose_name="Rôle", default=ETUDIANT)
    email = models.EmailField(unique=True, verbose_name="Adresse email")
    photo_profil = models.ImageField(upload_to='profils/', null=True, blank=True)  # Un seul champ photo_profil
    date_inscription = models.DateTimeField(auto_now_add=False, default=timezone.now)

    # Champs pour OAuth
    fournisseur_oauth = models.CharField(max_length=20, blank=True, null=True, 
                                         verbose_name="Fournisseur OAuth")
    identifiant_oauth = models.CharField(max_length=100, blank=True, null=True, 
                                         verbose_name="ID OAuth")

    # Champs de l'utilisateur
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    matricule = models.CharField(max_length=20, unique=True)

    # Configuration du modèle
    username = None  # Nous utilisons l'email comme identifiant principal
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'matricule']  # Le matricule est obligatoire

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"


class Classe(models.Model):
    """
    Groupes d'étudiants supervisés par un professeur
    """
    nom = models.CharField(max_length=100, verbose_name="Nom de la classe")
    code = models.CharField(max_length=20, unique=True, verbose_name="Code de la classe")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    # Relations
    professeur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, 
                                 limit_choices_to={'role': Utilisateur.PROFESSEUR},
                                 related_name='classes_enseignees',
                                 verbose_name="Professeur responsable")
    professeurs_supplementaires = models.ManyToManyField(
        Utilisateur,
        related_name='classes_enseignees_supplementaires',
        limit_choices_to={'role': Utilisateur.PROFESSEUR},
        blank=True,
        verbose_name="Professeurs supplémentaires"
    )
    etudiants = models.ManyToManyField(Utilisateur, 
                                      limit_choices_to={'role': Utilisateur.ETUDIANT},
                                      related_name='classes',
                                      verbose_name="Étudiants inscrits")
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    est_active = models.BooleanField(default=True, verbose_name="Classe active")
    
    class Meta:
        verbose_name = "Classe"
        verbose_name_plural = "Classes"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom

class Exercice(models.Model):
    """
    Exercices créés par les professeurs pour évaluer les étudiants
    """
    DIFFICULTE_CHOICES = [
        ('Facile', 'Facile'),
        ('Moyenne', 'Moyenne'),
        ('Difficile', 'Difficile'),
    ]
    titre = models.CharField(max_length=200, verbose_name="Titre de l'exercice")
    description = models.TextField(verbose_name="Description détaillée")
    consignes = models.TextField(verbose_name="Consignes pour les étudiants")
    fichier_pdf = models.FileField(
        upload_to='exercices/',
        null=False,  # Rendre obligatoire
        blank=False,
        verbose_name="Fichier PDF",
        validators=[FileExtensionValidator(['pdf'])]  # Uniquement PDF
    )  # <- ce champ doit exister

    # Relations
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, 
                             related_name='exercices',
                             verbose_name="Classe concernée")

    professeur = models.ForeignKey(Utilisateur, null=True, blank=True, on_delete=models.CASCADE)


    # Fichiers et dates
    fichier_consigne = models.FileField(
        upload_to='exercices/consignes/',
        validators=[FileExtensionValidator(['pdf', 'docx', 'txt'])],
        null=True, 
        blank=True,
        verbose_name="Fichier d'énoncé"
    )
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_limite = models.DateTimeField(null=True, blank=True, verbose_name="Date limite de rendu")
    
    # Configuration IA
    modele_correction = models.FileField(
        upload_to='modeles_correction/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx'])],
        verbose_name="Modèle de correction"
    )

    def save(self, *args, **kwargs):
        # Assurer que le modèle est bien téléchargé et disponible pour la correction par l'IA
        if self.modele_correction:
            # Déclencher la gestion du modèle d'IA (cela peut être un signal ou une tâche asynchrone)
            pass
        super().save(*args, **kwargs)
    # Statut
    est_publie = models.BooleanField(default=False, verbose_name="Publié aux étudiants")
    
    coefficient = models.FloatField(
        default=1.0,
        verbose_name="Coefficient",
        validators=[MinValueValidator(0.1), MaxValueValidator(5.0)]
    )
    difficulte = models.CharField(
        max_length=10,
        choices=DIFFICULTE_CHOICES,
        default='Moyenne',
        verbose_name="Niveau de difficulté"
    )
    class Meta:
        verbose_name = "Exercice"
        verbose_name_plural = "Exercices"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.titre} ({self.classe})"

class Soumission(models.Model):
    exercice = models.ForeignKey('Exercice', on_delete=models.CASCADE, related_name='soumissions')
    etudiant = models.ForeignKey('Utilisateur', on_delete=models.CASCADE, related_name='soumissions',
                                 limit_choices_to={'role': 'etudiant'})

    fichier_pdf = models.FileField(upload_to='soumissions/', validators=[FileExtensionValidator(['pdf'])])
    nom_original = models.CharField(max_length=255)
    taille_fichier = models.PositiveIntegerField()

    date_soumission = models.DateTimeField(auto_now_add=True)
    en_retard = models.BooleanField(default=False)
    ip_soumission = models.GenericIPAddressField(null=True, blank=True)

    est_plagiat = models.BooleanField(default=False)
    score_plagiat = models.FloatField(null=True, blank=True)
    empreinte_texte = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('exercice', 'etudiant')
        ordering = ['-date_soumission']

    def __str__(self):
        return f"Soumission de {self.etudiant} pour {self.exercice}"

    def save(self, *args, **kwargs):
        # ⚠️ Vérifie si retard
        if self.exercice.date_limite and timezone.now() > self.exercice.date_limite:
            self.en_retard = True

        if self.fichier_pdf and not self.taille_fichier:
            self.nom_original = self.fichier_pdf.name

            # 🔐 Lecture + chiffrement
            original_data = self.fichier_pdf.read()
            fernet = Fernet(settings.ENCRYPTION_KEY)
            encrypted_data = fernet.encrypt(original_data)

            # Remplace le fichier par version chiffrée
            encrypted_file = ContentFile(encrypted_data)
            self.fichier_pdf.save(self.fichier_pdf.name, encrypted_file, save=False)
            self.taille_fichier = len(encrypted_data)

        super().save(*args, **kwargs)

    def get_pdf_dechiffre(self):
        try:
            fernet = Fernet(settings.ENCRYPTION_KEY)
            with open(self.fichier_pdf.path, 'rb') as f:
                encrypted_data = f.read()
            return fernet.decrypt(encrypted_data)
        except Exception as e:
            print(f"Erreur de déchiffrement : {e}")
            return None

    def extraire_texte_pdf(self):
        try:
            pdf_bytes = self.get_pdf_dechiffre()
            if not pdf_bytes:
                return ""

            buffer = BytesIO(pdf_bytes)
            doc = fitz.open(stream=buffer, filetype="pdf")
            texte = ""
            for page in doc:
                texte += page.get_text()
            doc.close()
            return texte.strip()
        except Exception as e:
            print(f"❌ Erreur extraction texte : {e}")
            return "" 
class Correction(models.Model):
    """
    Corrections générées par l'IA et potentiellement modifiées par les professeurs
    """
    soumission = models.OneToOneField(Soumission, on_delete=models.CASCADE, related_name='correction', verbose_name="Soumission associée")
    
    note = models.FloatField(verbose_name="Note sur 20")
    feedback = models.TextField(verbose_name="Retour détaillé")
    points_forts = models.TextField(verbose_name="Points forts identifiés")
    points_faibles = models.TextField(verbose_name="Points à améliorer")
    
    modele_ia_utilise = models.CharField(max_length=100, verbose_name="Modèle d'IA utilisé")
    date_generation = models.DateTimeField(auto_now_add=True, verbose_name="Date de génération")
    temps_correction = models.FloatField(null=True, blank=True, verbose_name="Temps de correction (secondes)")
    parametres_ia = models.JSONField(default=dict, verbose_name="Paramètres utilisés par l'IA")
    
    est_validee = models.BooleanField(default=False, verbose_name="Validée par le professeur")
    commentaire_professeur = models.TextField(blank=True, null=True, verbose_name="Commentaire du professeur")
    date_validation = models.DateTimeField(null=True, blank=True, verbose_name="Date de validation")

    contenu_brut = models.TextField(blank=True, null=True, verbose_name="Réponse brute de l'IA (non parsée)")

    class Meta:
        verbose_name = "Correction"
        verbose_name_plural = "Corrections"
        ordering = ['-date_generation']
    
    def __str__(self):
        return f"Correction de {self.soumission} ({self.note}/20)"


class PerformanceEtudiant(models.Model):
    """
    Suivi des performances des étudiants sur les exercices
    """
    # Relations
    etudiant = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, 
                               limit_choices_to={'role': Utilisateur.ETUDIANT},
                               related_name='performances',
                               verbose_name="Étudiant")
    exercice = models.ForeignKey(Exercice, on_delete=models.CASCADE,
                               related_name='performances',
                               verbose_name="Exercice concerné")
    
    # Résultats
    note = models.FloatField(verbose_name="Note obtenue")
    moyenne_classe = models.FloatField(verbose_name="Moyenne de la classe")
    ecart_type = models.FloatField(verbose_name="Écart-type des notes")
    rang = models.IntegerField(verbose_name="Rang dans la classe")
    
    # Analyse
    temps_passe = models.FloatField(null=True, blank=True, 
                                  verbose_name="Temps passé (minutes)")
    suggestions_amelioration = models.TextField(verbose_name="Suggestions d'amélioration")
    competences_evaluees = models.JSONField(default=list, 
                                          verbose_name="Compétences évaluées")
    
    # Métadonnées
    date_mise_a_jour = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    class Meta:
        verbose_name = "Performance étudiant"
        verbose_name_plural = "Performances étudiant"
        unique_together = ('etudiant', 'exercice')
        ordering = ['-date_mise_a_jour']
    
    def __str__(self):
        return f"Performance de {self.etudiant} sur {self.exercice}"

class Notification(models.Model):
    """
    Notifications envoyées aux utilisateurs
    """
    # Types de notifications
    TYPE_CHOICES = [
        ('nouveau_exercice', 'Nouvel exercice disponible'),
        ('correction_disponible', 'Correction disponible'),
        ('retard', 'Soumission en retard'),
        ('message', 'Message personnel'),
        ('systeme', 'Notification système'),
    ]
    
    # Relation
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE,
                                  related_name='notifications',
                                  verbose_name="Destinataire")
    
    # Contenu
    message = models.TextField(verbose_name="Contenu du message")
    type_notification = models.CharField(max_length=50, choices=TYPE_CHOICES,
                                       verbose_name="Type de notification")
    lien = models.URLField(blank=True, null=True, verbose_name="Lien associé")
    
    # Statut
    est_lue = models.BooleanField(default=False, verbose_name="Lu")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date d'envoi")
    date_lecture = models.DateTimeField(null=True, blank=True, verbose_name="Date de lecture")
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Notification pour {self.utilisateur}"

class HistoriqueConnexion(models.Model):
    """
    Journal des connexions des utilisateurs
    """
    # Relation
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE,
                                  related_name='historique_connexions',
                                  verbose_name="Utilisateur")
    
    # Données techniques
    adresse_ip = models.GenericIPAddressField(verbose_name="Adresse IP")
    user_agent = models.CharField(max_length=255, verbose_name="Navigateur utilisé")
    reussie = models.BooleanField(default=True, verbose_name="Connexion réussie")
    
    # Métadonnées
    date_connexion = models.DateTimeField(auto_now_add=True, verbose_name="Date et heure de connexion")
    
    class Meta:
        verbose_name = "Historique de connexion"
        verbose_name_plural = "Historiques de connexion"
        ordering = ['-date_connexion']
    
    def __str__(self):
        statut = "réussie" if self.reussie else "échouée"
        return f"Connexion {statut} de {self.utilisateur} le {self.date_connexion}"

class ModeleCorrection(models.Model):
    """
    Modèles de correction utilisés par l'IA
    """
    nom = models.CharField(max_length=100, verbose_name="Nom du modèle")
    description = models.TextField(verbose_name="Description")
    contenu = models.TextField(verbose_name="Contenu du modèle")
    version = models.CharField(max_length=20, verbose_name="Version")
    
    # Relation
    professeur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE,
                                 limit_choices_to={'role': Utilisateur.PROFESSEUR},
                                 related_name='modeles_correction',
                                 verbose_name="Créateur")
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_mise_a_jour = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    est_actif = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = "Modèle de correction"
        verbose_name_plural = "Modèles de correction"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.nom} (v{self.version})"

class ParametresPlateforme(models.Model):
    """
    Paramètres globaux de la plateforme
    """
    nom_plateforme = models.CharField(max_length=100, default="Plateforme d'évaluation", 
                                    verbose_name="Nom de la plateforme")
    logo = models.URLField(blank=True, null=True, verbose_name="URL du logo")
    mode_maintenance = models.BooleanField(default=False, verbose_name="Mode maintenance")
    
    # Configuration fichiers
    taille_max_fichier = models.IntegerField(default=10, 
                                           verbose_name="Taille max des fichiers (MB)")
    extensions_autorisees = models.CharField(max_length=100, default="pdf,docx,txt", 
                                           verbose_name="Extensions autorisées")
    
    # Configuration IA
    modele_ia_par_defaut = models.CharField(max_length=100, blank=True, null=True,
                                          verbose_name="Modèle IA par défaut")
    
    class Meta:
        verbose_name = "Paramètre plateforme"
        verbose_name_plural = "Paramètres plateforme"
    
    def __str__(self):
        return "Configuration de la plateforme"
    
    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'une seule instance
        self.__class__.objects.exclude(id=self.id).delete()
        super().save(*args, **kwargs)

def update_correction_model(professor_feedback, correction_id):
    """
    Permet au professeur de valider ou ajuster la correction générée par l'IA.
    Les ajustements sont enregistrés pour affiner l'algorithme d'IA.
    """
    correction = Correction.objects.get(id=correction_id)
    
    # Appliquer le feedback du professeur sur l'évaluation
    correction.commentaire_professeur = professor_feedback
    correction.save()

    # Utiliser le feedback pour améliorer l'IA (logique d'apprentissage)
    retrain_ai_model(professor_feedback)  # Appeler la fonction de réentraînement de l'IA


    
    
def retrain_ai_model(professor_feedback):
    """
    Exemple d'une fonction pour réentraîner le modèle d'IA basé sur le feedback du professeur.
    Cette fonction peut être ajustée pour appeler un service externe d'IA ou pour 
    entraîner un modèle localement.
    """
    # Sauvegarder le feedback dans la base de données pour analyse future
    feedback_entry = Feedback(feedback_text=professor_feedback)
    feedback_entry.save()

    # Logique d'apprentissage (si nécessaire) : exemple de réentraînement via un modèle local ou API
    print(f"Feedback reçu pour réentraînement du modèle : {professor_feedback}")
    
    # Si tu utilises une API distante pour réentraîner, ajoute ici l'appel à l'API d'IA
    # Par exemple :
    # url = "https://api.deepseek.com/retrain_model"
    # data = {"feedback": professor_feedback}
    # response = requests.post(url, json=data)
    
    # Si tu utilises un modèle local, tu peux aussi réentraîner ton modèle avec les données récupérées
    # Exemple : appel à un script de réentraînement local
    # subprocess.run(["python3", "scripts/retrain_model.py", "--feedback", professor_feedback])


class Feedback(models.Model):
    feedback_text = models.TextField(verbose_name="Feedback du professeur")
    date_received = models.DateTimeField(auto_now_add=True, verbose_name="Date de réception")
    
    def __str__(self):
        return f"Feedback reçu le {self.date_received}"