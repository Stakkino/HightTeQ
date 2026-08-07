from rest_framework import serializers
from .models import Utilisateur

class InscriptionSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Utilisateur
        fields = ['id', 'username', 'password', 'telephone', 'email']

    def create(self, validated_data):
        # role forcé à 'client' ici, jamais lu depuis la requête
        return Utilisateur.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            telephone=validated_data['telephone'],
            email=validated_data.get('email', ''),
            role='client'
        )

class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ['id', 'username', 'telephone', 'email', 'role']