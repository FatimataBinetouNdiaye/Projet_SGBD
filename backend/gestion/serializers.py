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
        fields = ['id', 'username', 'email', 'password', 'role', 'photo_profil', 'date_inscription', 'matricule']
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


class ExerciceListSerializer(serializers.ModelSerializer):
    classe_nom = serializers.CharField(source='classe.nom', read_only=True)
    soumissions_count = serializers.IntegerField(source='soumissions.count', read_only=True)
    est_en_retard = serializers.SerializerMethodField()
    
    class Meta:
        model = Exercice
        fields = [
            'id', 'titre', 'description', 'classe', 'classe_nom',
            'date_limite', 'est_publie', 'soumissions_count', 'est_en_retard'
        ]
    
    def get_est_en_retard(self, obj):
        return obj.date_limite < timezone.now() if obj.date_limite else False


from django.core.validators import FileExtensionValidator

class CorrectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Correction
        fields = ['id', 'note', 'feedback', 'points_forts', 'points_faibles']


class SoumissionSerializer(serializers.ModelSerializer):
    correction = CorrectionSerializer(read_only=True)


    class Meta:
        model = Soumission
        fields = [
            'id', 'fichier_pdf', 'nom_original', 'taille_fichier',
            'date_soumission', 'en_retard', 'ip_soumission',
            'est_plagiat', 'score_plagiat', 'empreinte_texte',
            'exercice', 'etudiant',
            'correction'
        ]
        read_only_fields = ('etudiant', 'date_soumission')


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
            'professeur', 'professeur_nom', 'classe' , 'classe_nom',
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

    def validate(self, data):
        if 'date_limite' in data and data['date_limite'] < timezone.now():
            raise serializers.ValidationError({
                'date_limite': "La date limite est déjà passée"
            })
        
        if self.instance and self.instance.est_publie:
            if 'date_limite' in data and data['date_limite'] != self.instance.date_limite:
                raise serializers.ValidationError({
                    'date_limite': "Impossible de modifier la date limite après publication"
                })
        
        return data

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


class RecentSubmissionSerializer(serializers.ModelSerializer):
    exercice_titre = serializers.CharField(source='exercice.titre')
    
    class Meta:
        model = Soumission
        fields = ['id', 'exercice_titre', 'date_soumission', 'score']


from rest_framework import serializers
from .models import Soumission

class RecentSubmissionSerializer(serializers.ModelSerializer):
    exercise_title = serializers.CharField(source='exercice.titre')
    submission_date = serializers.DateTimeField(source='date_soumission')
    score = serializers.SerializerMethodField()
    exercise_id = serializers.IntegerField(source='exercice.id')

    class Meta:
        model = Soumission
        fields = [
            'id',
            'exercise_title',
            'submission_date', 
            'score',
            'exercise_id'
        ]

    def get_score(self, obj):
        if hasattr(obj, 'correction'):
            return obj.correction.note
        return None

class NextDeadlineSerializer(serializers.Serializer):
    exercise_id = serializers.IntegerField()
    exercise_title = serializers.CharField()
    deadline_date = serializers.DateTimeField()
    days_left = serializers.IntegerField()

class DashboardStatsSerializer(serializers.Serializer):
    completed = serializers.IntegerField()
    total = serializers.IntegerField()
    average_score = serializers.FloatField()
    next_deadline = NextDeadlineSerializer(allow_null=True)

class DashboardSerializer(serializers.Serializer):
    stats = DashboardStatsSerializer()
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