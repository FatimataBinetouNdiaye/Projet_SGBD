from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Utilisateur, Classe, Exercice, Soumission, Correction, PerformanceEtudiant
from django.utils import timezone
from rest_framework import serializers
from django.utils import timezone
from django.core.validators import FileExtensionValidator

class UtilisateurSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        app_label = 'gestion'
        model = Utilisateur
        fields = ['id', 'username', 'email', 'password', 'role', 'photo_profil', 'date_inscription', 'matricule','first_name', 'last_name']
        read_only_fields = ['date_inscription']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }
    
    def validate_email(self, value):
        if Utilisateur.objects.filter(email=value).exists():
            raise serializers.ValidationError("Un utilisateur avec cet email existe déjà.")
        return value
    
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.pop('password'))
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data.pop('password'))
        return super().update(instance, validated_data)



class ClasseSerializer(serializers.ModelSerializer):
    professeur_nom = serializers.CharField(source='professeur.get_full_name', read_only=True)
    etudiants_count = serializers.IntegerField(source='etudiants.count', read_only=True)
    
    class Meta:
        model = Classe
        fields = [
            'id', 'nom', 'code', 'description', 
            'professeur', 'professeur_nom', 'etudiants', 
            'etudiants_count', 'date_creation'
        ]
        read_only_fields = ['date_creation']


from rest_framework import serializers
from django.conf import settings

from rest_framework import serializers
from django.utils import timezone
from .models import Exercice

class ExerciceListSerializer(serializers.ModelSerializer):
    classe_nom = serializers.CharField(source='classe.nom', read_only=True)
    professeur_nom = serializers.SerializerMethodField()
    fichier_pdf_url = serializers.SerializerMethodField()
    fichier_consigne_url = serializers.SerializerMethodField()
    est_en_retard = serializers.SerializerMethodField()

    class Meta:
        model = Exercice
        fields = [
            'id', 'titre', 'description', 'consignes', 'classe', 'classe_nom',
            'professeur', 'professeur_nom', 'date_creation', 'date_limite',
            'est_publie', 'est_en_retard', 'fichier_pdf_url', 'fichier_consigne_url'
        ]

    def get_professeur_nom(self, obj):
        return f"{obj.professeur.first_name} {obj.professeur.last_name}" if obj.professeur else None

    

    def get_fichier_pdf_url(self, obj):
        print(f"Debug - Fichier PDF existe: {bool(obj.fichier_pdf)}")  # Vérifiez si le fichier existe
        if obj.fichier_pdf:
            try:
                url = obj.fichier_pdf.url
                request = self.context.get('request')
                if request:
                    full_url = request.build_absolute_uri(url)
                    print(f"Debug - URL générée: {full_url}")  # Vérifiez l'URL générée
                    return full_url
                return url
            except Exception as e:
                print(f"Erreur génération URL: {str(e)}")
        return None  # Explicitement retourner None si pas de fichier

    def get_fichier_consigne_url(self, obj):
        request = self.context.get('request')
        if obj.fichier_consigne and request:
            return request.build_absolute_uri(obj.fichier_consigne.url)
        return None

    def get_est_en_retard(self, obj):
        return obj.date_limite < timezone.now() if obj.date_limite else False

    

from django.core.validators import FileExtensionValidator

# 1. Serializer léger pour Soumission, avec titre de l’exercice
class SoumissionLightSerializer(serializers.ModelSerializer):
    exercice_title = serializers.CharField(source='exercice.titre', read_only=True)

    class Meta:
        model = Soumission
        fields = ['id', 'date_soumission', 'exercice_title']


# 2. CorrectionSerializer : inclut la soumission
class CorrectionSerializer(serializers.ModelSerializer):
    soumission = serializers.SerializerMethodField()
    plagiarism_report = serializers.SerializerMethodField()

    class Meta:
        model = Correction
        fields = '__all__'

    def get_soumission(self, obj):
        return {
            'id': obj.soumission.id,
            'etudiant_id': obj.soumission.etudiant.id,
            'exercice': {
                'id': obj.soumission.exercice.id if obj.soumission.exercice else None,
                'titre': obj.soumission.exercice.titre if obj.soumission.exercice else 'Titre inconnu'
            }
        }

    def get_plagiarism_report(self, obj):
        return obj.plagiarism_report or {}

# 3. SoumissionSerializer (inchangé sauf qu’il garde CorrectionSerializer)
class SoumissionSerializer(serializers.ModelSerializer):
    note = serializers.SerializerMethodField()
    feedback = serializers.SerializerMethodField()
    points_forts = serializers.SerializerMethodField()
    points_faibles = serializers.SerializerMethodField()
    commentaire_professeur = serializers.SerializerMethodField()

    class Meta:
        model = Soumission
        fields = [
            'id', 'fichier_pdf', 'nom_original', 'taille_fichier',
            'date_soumission', 'en_retard', 'ip_soumission',
            'est_plagiat', 'score_plagiat', 'empreinte_texte',
            'exercice', 'etudiant',
            'note', 'feedback', 'points_forts', 'points_faibles', 'commentaire_professeur'
        ]
        read_only_fields = ('etudiant', 'date_soumission')

    def get_note(self, obj):
        correction = getattr(obj, 'correction', None)
        return correction.note if correction else None

    def get_feedback(self, obj):
        correction = getattr(obj, 'correction', None)
        return correction.feedback if correction else ""

    def get_points_forts(self, obj):
        correction = getattr(obj, 'correction', None)
        return correction.points_forts if correction else ""

    def get_points_faibles(self, obj):
        correction = getattr(obj, 'correction', None)
        return correction.points_faibles if correction else ""

    def get_commentaire_professeur(self, obj):
        correction = getattr(obj, 'correction', None)
        return correction.commentaire_professeur if correction else ""


        
class ExerciceSerializer(serializers.ModelSerializer):
    soumissions = serializers.SerializerMethodField()
    professeur_nom = serializers.SerializerMethodField()
    peut_soumettre = serializers.SerializerMethodField()
    temps_restant = serializers.SerializerMethodField()
    est_expire = serializers.SerializerMethodField()

    class Meta:
        model = Exercice
        fields = [
            'id', 'titre', 'description', 'consignes', 
            'date_creation', 'date_limite', 'est_publie',
            'professeur', 'professeur_nom', 'classe' , 'classe_nom', 'difficulte',
            'fichier_pdf', 'modele_correction',
            'soumissions', 'peut_soumettre', 
            'temps_restant', 'est_expire'
        ]
        extra_kwargs = {
            'professeur': {'read_only': True},
            'date_creation': {'read_only': True},
            'fichier_pdf': {
                'required': False,
                'validators': [FileExtensionValidator(['pdf'])]
            },
            'modele_correction': {
                'required': False,
                'validators': [FileExtensionValidator(['pdf'])]
            }
        }

    def get_professeur_nom(self, obj):
        return obj.professeur.get_full_name()

    def get_peut_soumettre(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return (
                obj.est_publie and 
                obj.date_limite and obj.date_limite > timezone.now() and
                (request.user.role == Utilisateur.ETUDIANT or 
                 request.user == obj.professeur)
            )
        return False

    def get_temps_restant(self, obj):
        if obj.date_limite and obj.date_limite > timezone.now():
            delta = obj.date_limite - timezone.now()
            return {
                'jours': delta.days,
                'heures': delta.seconds // 3600,
                'minutes': (delta.seconds % 3600) // 60
            }
        return None

    def get_est_expire(self, obj):
        if obj.date_limite:
            return obj.date_limite < timezone.now()
        return False 

    classe_nom = serializers.CharField(source='classe.nom', read_only=True)  # Add this
    
    def get_soumissions(self, obj):
        try:
            request = self.context.get('request')
            if not request or not request.user.is_authenticated:
                return []
            
            # Debug:
            print(f"Getting submissions for exercise {obj.id}, user {request.user.id}")
            
            soumissions = obj.soumissions.select_related('etudiant')
            if request.user.role == Utilisateur.ETUDIANT:
                soumissions = soumissions.filter(etudiant=request.user)
            
            return SoumissionMiniSerializer(soumissions, many=True).data
            
        except Exception as e:
            print(f"Error in get_soumissions: {str(e)}")
            return []
            
    def validate_date_limite(self, value):
        if value < timezone.now():
            raise serializers.ValidationError(
                "La date limite doit être dans le futur"
            )
        return value

    

class SoumissionMiniSerializer(serializers.ModelSerializer):
    etudiant_nom = serializers.CharField(source='etudiant.get_full_name')
    
    class Meta:
        model = Soumission
        fields = [
            'id', 'date_soumission', 'en_retard',
            'etudiant', 'etudiant_nom', 'score_plagiat'
        ]

    



 


class PerformanceEtudiantSerializer(serializers.ModelSerializer):
    exercice_titre = serializers.CharField(source='exercice.titre', read_only=True)
    classe_nom = serializers.CharField(source='exercice.classe.nom', read_only=True)
    
    class Meta:
        model = PerformanceEtudiant
        fields = [
            'id', 'etudiant', 'exercice', 'exercice_titre', 'classe_nom',
            'note', 'moyenne_classe', 'ecart_type', 'rang',
            'temps_passe', 'suggestions_amelioration'
        ]


class DashboardStatsSerializer(serializers.Serializer):
    completed = serializers.IntegerField()
    total = serializers.IntegerField()
    average_score = serializers.FloatField()
    next_deadline = serializers.DictField()




from rest_framework import serializers
from .models import Soumission


class NextDeadlineSerializer(serializers.Serializer):
    exercise_id = serializers.IntegerField()
    exercise_title = serializers.CharField()
    deadline_date = serializers.DateTimeField()
    days_left = serializers.IntegerField()

from rest_framework import serializers
from .models import Soumission, Exercice

class NextDeadlineSerializer(serializers.Serializer):
    exercise_id = serializers.IntegerField()
    exercise_title = serializers.CharField()
    date_limite = serializers.DateTimeField()
    days_left = serializers.IntegerField()

from rest_framework import serializers
from .models import Soumission, Exercice
from django.utils import timezone

class NextDeadlineSerializer(serializers.Serializer):
    exercise_id = serializers.IntegerField()
    exercise_title = serializers.CharField()
    date_limite = serializers.DateTimeField()
    days_left = serializers.SerializerMethodField()

    def get_days_left(self, obj):
        return (obj['date_limite'] - timezone.now()).days

class RecentSubmissionSerializer(serializers.ModelSerializer):
    exercise_title = serializers.CharField(source='exercice.titre')
    submission_date = serializers.DateTimeField(source='date_soumission')
    correction = serializers.SerializerMethodField()  # Ajout de ce champ
    en_retard = serializers.BooleanField()
    est_plagiat = serializers.BooleanField()

    class Meta:
        model = Soumission
        fields = [
            'id',
            'exercise_title',
            'submission_date',
            'correction',  # Ajouté
            'en_retard',
            'est_plagiat',
            'nom_original'
        ]

    def get_correction(self, obj):
        if hasattr(obj, 'correction') and obj.correction:
            return {
                'note': obj.correction.note,
                'feedback': obj.correction.feedback,
                'points_forts': obj.correction.points_forts,
                'points_faibles': obj.correction.points_faibles,
                'commentaire_professeur': obj.correction.commentaire_professeur,
                'est_validee': obj.correction.est_validee
            }
        return None

class DashboardSerializer(serializers.Serializer):
    stats = serializers.DictField()
    recent_submissions = RecentSubmissionSerializer(many=True)



from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import serializers
from .models import Utilisateur
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomAuthTokenSerializer(AuthTokenSerializer):
    role = serializers.SerializerMethodField()
    
    def get_role(self, obj):
        return obj.user.role  # Retourne 'ET' ou 'PR'
    
    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = attrs['user']
        return {
            'token': attrs['token'],
            'user_id': user.id,
            'email': user.email,
            'role': user.role,
            'role_display': user.get_role_display(),
            'full_name': user.get_full_name()
        }
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'  # Si ton User utilise email comme identifiant
    
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email is None or password is None:
            raise serializers.ValidationError("Email et mot de passe requis.")

        # Ajoute ça pour éviter le KeyError
        attrs[self.username_field] = email

        # Appelle le parent
        data = super().validate(attrs)

        user = self.user
        data['user_id'] = user.id
        data['email'] = user.email
        data['role'] = self.user.role
        return data
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role  
        return token
    


from rest_framework import serializers


class StudentSerializer(serializers.ModelSerializer):
    classes = serializers.SerializerMethodField()
    
    class Meta:
        model = Utilisateur
        fields = [
            'id',
            'matricule',
            'last_name',
            'first_name',
            'email',
            'classes',
            'date_inscription'
        ]
    
    def get_classes(self, obj):
        return list(obj.classes.values_list('nom', flat=True))    
    


# serializers.py
class TeacherSubmissionSerializer(serializers.ModelSerializer):
    etudiant_nom = serializers.SerializerMethodField()
    etudiant_prenom = serializers.SerializerMethodField()
    exercice_titre = serializers.SerializerMethodField()
    classe_nom = serializers.SerializerMethodField()
    correction = serializers.SerializerMethodField()

    class Meta:
        model = Soumission
        fields = [
            'id',
            'etudiant_nom',
            'etudiant_prenom',
            'exercice_titre',
            'classe_nom',
            'date_soumission',
            'correction',
            'nom_original',
            'en_retard',
            'est_plagiat'
        ]

    def get_etudiant_nom(self, obj):
        return obj.etudiant.last_name if obj.etudiant else ''

    def get_etudiant_prenom(self, obj):
        return obj.etudiant.first_name if obj.etudiant else ''

    def get_exercice_titre(self, obj):
        return obj.exercice.titre if obj.exercice else ''

    def get_classe_nom(self, obj):
        return obj.exercice.classe.nom if obj.exercice and obj.exercice.classe else ''

    def get_correction(self, obj):
        if not hasattr(obj, 'correction') or not obj.correction:
            return None
            
        return {
            'id': obj.correction.id,
            'note': obj.correction.note,
            'note_ia': getattr(obj.correction, 'note_ia', None),
            'feedback': obj.correction.feedback,
            'points_forts': obj.correction.points_forts,
            'points_faibles': obj.correction.points_faibles,
            'commentaire_professeur': obj.correction.commentaire_professeur,
            'est_validee': obj.correction.est_validee,
            'date_validation': obj.correction.date_validation
        }


class PlagiarismDetailSerializer(serializers.Serializer):
    cosine = serializers.FloatField()
    jaccard = serializers.FloatField()
    text1_length = serializers.IntegerField()
    text2_length = serializers.IntegerField()

from rest_framework import serializers
from gestion.models import Correction

class PlagiarismReportSerializer(serializers.ModelSerializer):
    exercice_titre = serializers.CharField(source='soumission.exercice.titre', read_only=True)
    date_soumission = serializers.DateTimeField(source='soumission.date_soumission', read_only=True)
    
    class Meta:
        model = Correction
        fields = [
            'id',
            'note',  # Assurez-vous que ce champ existe dans le modèle Correction
            'exercice_titre',
            'date_soumission',
            'plagiarism_score',
            'plagiarism_report',
            'feedback',
            'points_forts',
            'points_faibles'
        ]
class CorrectionSerializer(serializers.ModelSerializer):
    plagiarism_report = PlagiarismReportSerializer(many=True)
    
    class Meta:
        model = Correction
        fields = [
            'id', 'soumission', 'note', 'feedback',
            'points_forts', 'points_faibles', 'contenu_brut',
            'plagiarism_report', 'plagiarism_score', 'est_plagiat'
        ]