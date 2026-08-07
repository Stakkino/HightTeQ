from rest_framework import serializers
from .models import Commande, LigneCommande

class LigneCommandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LigneCommande
        fields = ['id', 'produit', 'service', 'quantite', 'prix_unitaire']

class CommandeSerializer(serializers.ModelSerializer):
    lignes = LigneCommandeSerializer(many=True)

    class Meta:
        model = Commande
        fields = ['id', 'client', 'total_ariary', 'statut', 'message_whatsapp', 'date_creation', 'lignes']
        read_only_fields = ['client', 'statut']

    def create(self, validated_data):
        lignes_data = validated_data.pop('lignes')
        commande = Commande.objects.create(**validated_data)
        for ligne_data in lignes_data:
            LigneCommande.objects.create(commande=commande, **ligne_data)
        return commande