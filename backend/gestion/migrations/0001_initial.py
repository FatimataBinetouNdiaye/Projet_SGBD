
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Utilisateur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.CharField(choices=[('etudiant', 'Étudiant'), ('professeur', 'Professeur')], default='etudiant', max_length=20)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('matricule', models.CharField(max_length=20, unique=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Utilisateur',
                'verbose_name_plural': 'Utilisateurs',
                'ordering': ['last_name', 'first_name'],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Classe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, verbose_name='Nom de la classe')),
                ('code', models.CharField(max_length=20, unique=True, verbose_name='Code de la classe')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('est_active', models.BooleanField(default=True, verbose_name='Classe active')),
                ('etudiants', models.ManyToManyField(limit_choices_to={'role': 'ET'}, related_name='classes', to=settings.AUTH_USER_MODEL, verbose_name='Étudiants inscrits')),
                ('professeur', models.ForeignKey(limit_choices_to={'role': 'PR'}, on_delete=django.db.models.deletion.CASCADE, related_name='classes_enseignees', to=settings.AUTH_USER_MODEL, verbose_name='Professeur responsable')),
            ],
            options={
                'verbose_name': 'Classe',
                'verbose_name_plural': 'Classes',
                'ordering': ['nom'],
            },
        ),
        migrations.CreateModel(
            name='Exercice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(max_length=200, verbose_name="Titre de l'exercice")),
                ('description', models.TextField(verbose_name='Description détaillée')),
                ('consignes', models.TextField(verbose_name='Consignes pour les étudiants')),
                ('fichier_consigne', models.FileField(blank=True, null=True, upload_to='exercices/consignes/', validators=[django.core.validators.FileExtensionValidator(['pdf', 'docx', 'txt'])], verbose_name="Fichier d'énoncé")),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('date_limite', models.DateTimeField(blank=True, null=True, verbose_name='Date limite de rendu')),
                ('modele_correction', models.TextField(verbose_name="Modèle de correction pour l'IA")),
                ('ponderation', models.JSONField(default=dict, verbose_name='Pondération des critères')),
                ('est_publie', models.BooleanField(default=False, verbose_name='Publié aux étudiants')),
                ('classe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exercices', to='gestion.classe', verbose_name='Classe concernée')),
                ('professeur', models.ForeignKey(limit_choices_to={'role': 'PR'}, on_delete=django.db.models.deletion.CASCADE, related_name='exercices_crees', to=settings.AUTH_USER_MODEL, verbose_name='Professeur créateur')),
            ],
            options={
                'verbose_name': 'Exercice',
                'verbose_name_plural': 'Exercices',
                'ordering': ['-date_creation'],
            },
        ),
        migrations.CreateModel(
            name='ParametresPlateforme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_plateforme', models.CharField(default="Plateforme d'évaluation", max_length=100, verbose_name='Nom de la plateforme')),
                ('logo', models.URLField(blank=True, null=True, verbose_name='URL du logo')),
                ('mode_maintenance', models.BooleanField(default=False, verbose_name='Mode maintenance')),
                ('taille_max_fichier', models.IntegerField(default=10, verbose_name='Taille max des fichiers (MB)')),
                ('extensions_autorisees', models.CharField(default='pdf,docx,txt', max_length=100, verbose_name='Extensions autorisées')),
                ('modele_ia_par_defaut', models.CharField(blank=True, max_length=100, null=True, verbose_name='Modèle IA par défaut')),
            ],
            options={
                'verbose_name': 'Paramètre plateforme',
                'verbose_name_plural': 'Paramètres plateforme',
            },
        ),
        migrations.CreateModel(
            name='Soumission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fichier_pdf', models.FileField(upload_to='soumissions/', validators=[django.core.validators.FileExtensionValidator(['pdf'])], verbose_name='Fichier PDF rendu')),
                ('nom_original', models.CharField(max_length=255, verbose_name='Nom original du fichier')),
                ('taille_fichier', models.PositiveIntegerField(verbose_name='Taille du fichier (octets)')),
                ('date_soumission', models.DateTimeField(auto_now_add=True, verbose_name='Date de soumission')),
                ('en_retard', models.BooleanField(default=False, verbose_name='Rendu en retard')),
                ('ip_soumission', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP de soumission')),
                ('est_plagiat', models.BooleanField(default=False, verbose_name='Suspecté de plagiat')),
                ('score_plagiat', models.FloatField(blank=True, null=True, verbose_name='Score de similarité')),
                ('empreinte_texte', models.TextField(blank=True, null=True, verbose_name='Empreinte textuelle')),
                ('etudiant', models.ForeignKey(limit_choices_to={'role': 'ET'}, on_delete=django.db.models.deletion.CASCADE, related_name='soumissions', to=settings.AUTH_USER_MODEL, verbose_name='Étudiant')),
                ('exercice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='soumissions', to='gestion.exercice', verbose_name='Exercice concerné')),
            ],
            options={
                'verbose_name': 'Soumission',
                'verbose_name_plural': 'Soumissions',
                'ordering': ['-date_soumission'],
                'unique_together': {('exercice', 'etudiant')},
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(verbose_name='Contenu du message')),
                ('type_notification', models.CharField(choices=[('nouveau_exercice', 'Nouvel exercice disponible'), ('correction_disponible', 'Correction disponible'), ('retard', 'Soumission en retard'), ('message', 'Message personnel'), ('systeme', 'Notification système')], max_length=50, verbose_name='Type de notification')),
                ('lien', models.URLField(blank=True, null=True, verbose_name='Lien associé')),
                ('est_lue', models.BooleanField(default=False, verbose_name='Lu')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name="Date d'envoi")),
                ('date_lecture', models.DateTimeField(blank=True, null=True, verbose_name='Date de lecture')),
                ('utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL, verbose_name='Destinataire')),
            ],
            options={
                'verbose_name': 'Notification',
                'verbose_name_plural': 'Notifications',
                'ordering': ['-date_creation'],
            },
        ),
        migrations.CreateModel(
            name='ModeleCorrection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, verbose_name='Nom du modèle')),
                ('description', models.TextField(verbose_name='Description')),
                ('contenu', models.TextField(verbose_name='Contenu du modèle')),
                ('version', models.CharField(max_length=20, verbose_name='Version')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('date_mise_a_jour', models.DateTimeField(auto_now=True, verbose_name='Date de mise à jour')),
                ('est_actif', models.BooleanField(default=True, verbose_name='Actif')),
                ('professeur', models.ForeignKey(limit_choices_to={'role': 'PR'}, on_delete=django.db.models.deletion.CASCADE, related_name='modeles_correction', to=settings.AUTH_USER_MODEL, verbose_name='Créateur')),
            ],
            options={
                'verbose_name': 'Modèle de correction',
                'verbose_name_plural': 'Modèles de correction',
                'ordering': ['-date_creation'],
            },
        ),
        migrations.CreateModel(
            name='HistoriqueConnexion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('adresse_ip', models.GenericIPAddressField(verbose_name='Adresse IP')),
                ('user_agent', models.CharField(max_length=255, verbose_name='Navigateur utilisé')),
                ('reussie', models.BooleanField(default=True, verbose_name='Connexion réussie')),
                ('date_connexion', models.DateTimeField(auto_now_add=True, verbose_name='Date et heure de connexion')),
                ('utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historique_connexions', to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur')),
            ],
            options={
                'verbose_name': 'Historique de connexion',
                'verbose_name_plural': 'Historiques de connexion',
                'ordering': ['-date_connexion'],
            },
        ),
        migrations.CreateModel(
            name='Correction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.FloatField(verbose_name='Note sur 20')),
                ('feedback', models.TextField(verbose_name='Retour détaillé')),
                ('points_forts', models.TextField(verbose_name='Points forts identifiés')),
                ('points_faibles', models.TextField(verbose_name='Points à améliorer')),
                ('modele_ia_utilise', models.CharField(max_length=100, verbose_name="Modèle d'IA utilisé")),
                ('date_generation', models.DateTimeField(auto_now_add=True, verbose_name='Date de génération')),
                ('temps_correction', models.FloatField(blank=True, null=True, verbose_name='Temps de correction (secondes)')),
                ('parametres_ia', models.JSONField(default=dict, verbose_name="Paramètres utilisés par l'IA")),
                ('est_validee', models.BooleanField(default=False, verbose_name='Validée par le professeur')),
                ('commentaire_professeur', models.TextField(blank=True, null=True, verbose_name='Commentaire du professeur')),
                ('date_validation', models.DateTimeField(blank=True, null=True, verbose_name='Date de validation')),
                ('soumission', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='correction', to='gestion.soumission', verbose_name='Soumission associée')),
            ],
            options={
                'verbose_name': 'Correction',
                'verbose_name_plural': 'Corrections',
                'ordering': ['-date_generation'],
            },
        ),
        migrations.CreateModel(
            name='PerformanceEtudiant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.FloatField(verbose_name='Note obtenue')),
                ('moyenne_classe', models.FloatField(verbose_name='Moyenne de la classe')),
                ('ecart_type', models.FloatField(verbose_name='Écart-type des notes')),
                ('rang', models.IntegerField(verbose_name='Rang dans la classe')),
                ('temps_passe', models.FloatField(blank=True, null=True, verbose_name='Temps passé (minutes)')),
                ('suggestions_amelioration', models.TextField(verbose_name="Suggestions d'amélioration")),
                ('competences_evaluees', models.JSONField(default=list, verbose_name='Compétences évaluées')),
                ('date_mise_a_jour', models.DateTimeField(auto_now=True, verbose_name='Date de mise à jour')),
                ('etudiant', models.ForeignKey(limit_choices_to={'role': 'ET'}, on_delete=django.db.models.deletion.CASCADE, related_name='performances', to=settings.AUTH_USER_MODEL, verbose_name='Étudiant')),
                ('exercice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='performances', to='gestion.exercice', verbose_name='Exercice concerné')),
            ],
            options={
                'verbose_name': 'Performance étudiant',
                'verbose_name_plural': 'Performances étudiant',
                'ordering': ['-date_mise_a_jour'],
                'unique_together': {('etudiant', 'exercice')},
            },
        ),
    ]
