from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Utilisateur, Classe, Exercice, Soumission, Correction, PerformanceEtudiant
from django.utils import timezone

class UtilisateurSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
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


class SoumissionSerializer(serializers.ModelSerializer):
    exercice_titre = serializers.CharField(source='exercice.titre', read_only=True)
    etudiant_nom = serializers.CharField(source='etudiant.get_full_name', read_only=True)
    
    class Meta:
        model = Soumission
        fields = [
            'id', 'exercice', 'exercice_titre', 'etudiant', 'etudiant_nom',
            'fichier_pdf', 'nom_original', 'taille_fichier', 'date_soumission',
            'en_retard', 'est_plagiat', 'score_plagiat'
        ]
        read_only_fields = [
            'etudiant', 'date_soumission', 'en_retard', 
            'est_plagiat', 'score_plagiat'
        ]
class ExerciceSerializer(serializers.ModelSerializer):
    soumissions = serializers.SerializerMethodField(read_only=True)
    professeur_nom = serializers.CharField(source='professeur.get_full_name', read_only=True)
    
    class Meta:
        model = Exercice
        fields = '__all__'
        extra_kwargs = {
           # 'professeur': {'read_only': True},  # Le professeur sera défini automatiquement
            'fichier_pdf': {'required': False},  # Rendre le PDF optionnel
            'deadline': {'required': True},      # Obligatoire
            'consignes': {'required': False},  # Rendre optionnel
            'modele_correction': {
                'required': False,
                'allow_null': True
            },
            'fichier_pdf': {
                'required': False,
                'validators': [FileExtensionValidator(['pdf'])]
            },
            'classe': {'required': False},
            'professeur': {'required': False}  # Rend le champ optionnel
        }
    def validate(self, data):
        # Validation personnalisée si nécessaire
        if 'deadline' in data and data['deadline'] < timezone.now():
            raise serializers.ValidationError({"deadline": "La date limite doit être dans le futur"})
        return data
    
    def get_soumissions(self, obj):
    # S'assurer que c'est bien une instance, pas un dict
        if isinstance(obj, dict):
            return []

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if request.user.role == Utilisateur.ETUDIANT:
                queryset = obj.soumissions.filter(etudiant=request.user)
            else:
                queryset = obj.soumissions.all()
            return SoumissionSerializer(queryset, many=True, context=self.context).data
        return []

    


class CorrectionSerializer(serializers.ModelSerializer):
    soumission_details = SoumissionSerializer(source='soumission', read_only=True)
    
    class Meta:
        model = Correction
        fields = [
            'id', 'soumission', 'soumission_details', 'note', 'feedback',
            'points_forts', 'points_faibles', 'est_validee',
            'commentaire_professeur', 'date_validation'
        ]
        read_only_fields = ['date_validation']


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
        token['role'] = user.role  # 👈 Ajoute le rôle dans le token
        return token