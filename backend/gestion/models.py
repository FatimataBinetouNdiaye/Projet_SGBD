from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import FileExtensionValidator



class User(AbstractUser):
    ROLE_CHOICES = (
        ('etudiant', 'Étudiant'),
        ('professeur', 'Professeur'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='etudiant')  # 👈 ici
    username = None

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    matricule = models.CharField(max_length=20, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'matricule']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Classe(models.Model):
    """
    Groupes d'étudiants supervisés par un professeur
    """
    nom = models.CharField(max_length=100, verbose_name="Nom de la classe")
    code = models.CharField(max_length=20, unique=True, verbose_name="Code de la classe")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    # Relations
    professeur = models.ForeignKey(User, on_delete=models.CASCADE, 
                                 limit_choices_to={'role': User.PROFESSEUR},
                                 related_name='classes_enseignees',
                                 verbose_name="Professeur responsable")
    etudiants = models.ManyToManyField(User, 
                                      limit_choices_to={'role': User.ETUDIANT},
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
    titre = models.CharField(max_length=200, verbose_name="Titre de l'exercice")
    description = models.TextField(verbose_name="Description détaillée")
    consignes = models.TextField(verbose_name="Consignes pour les étudiants")
    
    # Relations
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, 
                             related_name='exercices',
                             verbose_name="Classe concernée")
    professeur = models.ForeignKey(User, on_delete=models.CASCADE, 
                                 limit_choices_to={'role': User.PROFESSEUR},
                                 related_name='exercices_crees',
                                 verbose_name="Professeur créateur")
    
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
    modele_correction = models.TextField(verbose_name="Modèle de correction pour l'IA")
    ponderation = models.JSONField(default=dict, verbose_name="Pondération des critères")
    
    # Statut
    est_publie = models.BooleanField(default=False, verbose_name="Publié aux étudiants")
    
    class Meta:
        verbose_name = "Exercice"
        verbose_name_plural = "Exercices"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.titre} ({self.classe})"

class Soumission(models.Model):
    """
    Travaux rendus par les étudiants pour un exercice donné
    """
    # Relations
    exercice = models.ForeignKey(Exercice, on_delete=models.CASCADE, 
                               related_name='soumissions',
                               verbose_name="Exercice concerné")
    etudiant = models.ForeignKey(User, on_delete=models.CASCADE, 
                               limit_choices_to={'role': User.ETUDIANT},
                               related_name='soumissions',
                               verbose_name="Étudiant")
    
    # Fichier soumis
    fichier_pdf = models.FileField(
        upload_to='soumissions/',
        validators=[FileExtensionValidator(['pdf'])],
        verbose_name="Fichier PDF rendu"
    )
    nom_original = models.CharField(max_length=255, verbose_name="Nom original du fichier")
    taille_fichier = models.PositiveIntegerField(verbose_name="Taille du fichier (octets)")
    
    # Métadonnées
    date_soumission = models.DateTimeField(auto_now_add=True, verbose_name="Date de soumission")
    en_retard = models.BooleanField(default=False, verbose_name="Rendu en retard")
    ip_soumission = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP de soumission")
    
    # Analyse
    est_plagiat = models.BooleanField(default=False, verbose_name="Suspecté de plagiat")
    score_plagiat = models.FloatField(null=True, blank=True, verbose_name="Score de similarité")
    empreinte_texte = models.TextField(null=True, blank=True, verbose_name="Empreinte textuelle")
    
    class Meta:
        verbose_name = "Soumission"
        verbose_name_plural = "Soumissions"
        unique_together = ('exercice', 'etudiant')
        ordering = ['-date_soumission']
    
    def save(self, *args, **kwargs):
        # Vérification du retard
        if self.exercice.date_limite and timezone.now() > self.exercice.date_limite:
            self.en_retard = True
        
        # Calcul de la taille du fichier
        if self.fichier_pdf and not self.taille_fichier:
            self.taille_fichier = self.fichier_pdf.size
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Soumission de {self.etudiant} pour {self.exercice}"

class Correction(models.Model):
    """
    Corrections générées par l'IA et potentiellement modifiées par les professeurs
    """
    # Relation
    soumission = models.OneToOneField(Soumission, on_delete=models.CASCADE, 
                                    related_name='correction',
                                    verbose_name="Soumission associée")
    
    # Résultats
    note = models.FloatField(verbose_name="Note sur 20")
    feedback = models.TextField(verbose_name="Retour détaillé")
    points_forts = models.TextField(verbose_name="Points forts identifiés")
    points_faibles = models.TextField(verbose_name="Points à améliorer")
    
    # Métadonnées IA
    modele_ia_utilise = models.CharField(max_length=100, verbose_name="Modèle d'IA utilisé")
    date_generation = models.DateTimeField(auto_now_add=True, verbose_name="Date de génération")
    temps_correction = models.FloatField(null=True, blank=True, 
                                       verbose_name="Temps de correction (secondes)")
    parametres_ia = models.JSONField(default=dict, verbose_name="Paramètres utilisés par l'IA")
    
    # Validation professeur
    est_validee = models.BooleanField(default=False, verbose_name="Validée par le professeur")
    commentaire_professeur = models.TextField(blank=True, null=True, 
                                            verbose_name="Commentaire du professeur")
    date_validation = models.DateTimeField(null=True, blank=True, 
                                         verbose_name="Date de validation")
    
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
    etudiant = models.ForeignKey(User, on_delete=models.CASCADE, 
                               limit_choices_to={'role': User.ETUDIANT},
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
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE,
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
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE,
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
    professeur = models.ForeignKey(User, on_delete=models.CASCADE,
                                 limit_choices_to={'role': User.PROFESSEUR},
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

