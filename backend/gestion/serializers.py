from rest_framework import serializers

from .models import  User

from django.contrib.auth.hashers import make_password
from .models import *
from .models import Exercice, Soumission 

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'matricule', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')  # Retirer password2 avant la création
        validated_data['password'] = make_password(validated_data['password'])  # Hachage du mot de passe
        return User.objects.create(**validated_data)








class ClasseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classe
        fields = '__all__'
        extra_kwargs = {
            'professeur': {'required': True}  # Rend le champ obligatoire
        }

    def validate(self, data):
        if 'professeur' not in data:
            raise serializers.ValidationError(
                {"professeur": "Ce champ est obligatoire."}
            )
        return data

class ExerciceSerializer(serializers.ModelSerializer):
    classe_id = serializers.PrimaryKeyRelatedField(
        queryset=Classe.objects.all(),
        source='classe',
        write_only=True,
        required=True
    )
    
    class Meta:
        model = Exercice
        fields = ['id', 'titre', 'description', 'classe_id', 'date_limite', 'fichier_consigne']
        read_only_fields = ['professeur']

    def create(self, validated_data):
        # Associe automatiquement le professeur connecté
        validated_data['professeur'] = self.context['request'].user
        return super().create(validated_data)

class SoumissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Soumission
        fields = '__all__'
        read_only_fields = ('etudiant', 'date_soumission')

class CorrectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Correction
        fields = '__all__'

class PerformanceEtudiantSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceEtudiant
        fields = '__all__'

class SoumissionDetailSerializer(serializers.ModelSerializer):
    exercice = ExerciceSerializer()
    correction = CorrectionSerializer()
    
    class Meta:
        model = Soumission
        fields = '__all__'

class ExerciceWithSoumissionSerializer(serializers.ModelSerializer):
    soumission = serializers.SerializerMethodField()
    
    class Meta:
        model = Exercice
        fields = '__all__'
    
    def get_soumission(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            soumission = obj.soumissions.filter(etudiant=request.user).first()
            return SoumissionSerializer(soumission).data if soumission else None
        return None
    

    

