from rest_framework import serializers
from .models import Marque, Categorie, Produit, ImageProduit, AvisProduit


class ImageProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageProduit
        fields = ['id', 'image', 'legende', 'ordre']


class AvisProduitSerializer(serializers.ModelSerializer):
    note = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = AvisProduit
        fields = ['id', 'nom_client', 'note', 'commentaire', 'date_creation']
        read_only_fields = ['date_creation']
    
    def create(self, validated_data):
        # Récupérer l'ID du produit depuis le contexte
        produit_id = self.context.get('produit_id')
        if not produit_id:
            raise serializers.ValidationError("ID du produit requis")
        
        try:
            produit = Produit.objects.get(id=produit_id)
        except Produit.DoesNotExist:
            raise serializers.ValidationError("Produit non trouvé")
        
        return AvisProduit.objects.create(produit=produit, **validated_data)


class MarqueSerializer(serializers.ModelSerializer):
    nombre_produits = serializers.SerializerMethodField()
    
    class Meta:
        model = Marque
        fields = ['id', 'nom', 'logo', 'description', 'site_web', 'nombre_produits']
    
    def get_nombre_produits(self, obj):
        return obj.produits.filter(est_actif=True).count()


class CategorieSimpleSerializer(serializers.ModelSerializer):
    """Sérialiseur léger pour les sous-catégories"""
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'slug']


class CategorieSerializer(serializers.ModelSerializer):
    sous_categories = CategorieSimpleSerializer(many=True, read_only=True)
    nombre_produits = serializers.SerializerMethodField()
    
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'slug', 'description', 'image', 'sous_categories', 'nombre_produits']
    
    def get_nombre_produits(self, obj):
        return obj.produits.filter(est_actif=True).count()


class ProduitListeSerializer(serializers.ModelSerializer):
    """Sérialiseur léger pour la liste des produits"""
    marque_nom = serializers.CharField(source='marque.nom', read_only=True)
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    prix_actuel = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    en_promotion = serializers.BooleanField(read_only=True)
    pourcentage_reduction = serializers.IntegerField(read_only=True)
    note_moyenne = serializers.SerializerMethodField()
    
    class Meta:
        model = Produit
        fields = [
            'id', 'nom', 'slug', 'marque_nom', 'categorie_nom',
            'prix_ariary', 'prix_actuel', 'en_promotion', 'pourcentage_reduction',
            'image', 'badge', 'stock', 'note_moyenne', 'date_creation'
        ]
    
    def get_note_moyenne(self, obj):
        avis = obj.avis.filter(est_approuve=True)
        if avis.exists():
            return round(avis.aggregate(models.Avg('note'))['note__avg'], 1)
        return None


class ProduitDetailSerializer(serializers.ModelSerializer):
    """Sérialiseur complet pour le détail d'un produit"""
    marque = MarqueSerializer(read_only=True)
    categorie = CategorieSimpleSerializer(read_only=True)
    images = ImageProduitSerializer(many=True, read_only=True)
    prix_actuel = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    en_promotion = serializers.BooleanField(read_only=True)
    pourcentage_reduction = serializers.IntegerField(read_only=True)
    note_moyenne = serializers.SerializerMethodField()
    nombre_avis = serializers.SerializerMethodField()
    avis_recents = serializers.SerializerMethodField()
    
    class Meta:
        model = Produit
        fields = [
            'id', 'nom', 'slug', 'marque', 'categorie',
            'description', 'caracteristiques', 'prix_ariary',
            'prix_promo_ariary', 'prix_actuel', 'en_promotion',
            'pourcentage_reduction', 'stock', 'image', 'badge',
            'est_disponible', 'poids_kg', 'images',
            'note_moyenne', 'nombre_avis', 'avis_recents',
            'date_creation', 'date_modification'
        ]
    
    def get_note_moyenne(self, obj):
        avis = obj.avis.filter(est_approuve=True)
        if avis.exists():
            return round(avis.aggregate(models.Avg('note'))['note__avg'], 1)
        return None
    
    def get_nombre_avis(self, obj):
        return obj.avis.filter(est_approuve=True).count()
    
    def get_avis_recents(self, obj):
        avis = obj.avis.filter(est_approuve=True)[:5]
        return AvisProduitSerializer(avis, many=True).data


class ProduitCreateUpdateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour créer/modifier un produit (admin)"""
    class Meta:
        model = Produit
        fields = [
            'nom', 'marque', 'categorie', 'description', 'caracteristiques',
            'prix_ariary', 'prix_promo_ariary', 'stock', 'image',
            'badge', 'est_actif', 'est_en_vedette', 'poids_kg'
        ]