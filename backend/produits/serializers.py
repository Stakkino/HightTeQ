from rest_framework import serializers
from .models import Marque, Categorie, Produit

class MarqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marque
        fields = ['id', 'nom', 'logo']

class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'slug']

class ProduitSerializer(serializers.ModelSerializer):
    marque = MarqueSerializer(read_only=True)
    categorie = CategorieSerializer(read_only=True)

    class Meta:
        model = Produit
        fields = ['id', 'nom', 'marque', 'categorie', 'description', 'prix_ariary', 'stock', 'image', 'badge', 'date_creation']