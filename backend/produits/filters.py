import django_filters
from .models import Produit, Categorie


class ProduitFilter(django_filters.FilterSet):
    """Filtres pour l'API de recherche de produits"""
    
    # Filtre par prix
    prix_min = django_filters.NumberFilter(field_name="prix_ariary", lookup_expr='gte')
    prix_max = django_filters.NumberFilter(field_name="prix_ariary", lookup_expr='lte')
    
    # Filtre par catégorie
    categorie = django_filters.CharFilter(field_name='categorie__slug')
    
    # Filtre par marque
    marque = django_filters.NumberFilter(field_name='marque__id')
    
    # Filtre de recherche textuelle
    recherche = django_filters.CharFilter(method='filter_recherche')
    
    # Filtre par disponibilité
    en_stock = django_filters.BooleanFilter(method='filter_en_stock')
    
    # Filtre par badge
    badge = django_filters.CharFilter(field_name='badge')
    
    # Filtre par promotion
    en_promotion = django_filters.BooleanFilter(method='filter_en_promotion')
    
    class Meta:
        model = Produit
        fields = ['categorie', 'marque', 'badge', 'est_en_vedette']
    
    def filter_recherche(self, queryset, name, value):
        return queryset.filter(
            models.Q(nom__icontains=value) |
            models.Q(description__icontains=value) |
            models.Q(marque__nom__icontains=value)
        )
    
    def filter_en_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__gt=0)
        return queryset.filter(stock=0)
    
    def filter_en_promotion(self, queryset, name, value):
        if value:
            return queryset.filter(
                prix_promo_ariary__isnull=False,
                prix_promo_ariary__lt=models.F('prix_ariary')
            )
        return queryset.filter(
            models.Q(prix_promo_ariary__isnull=True) |
            models.Q(prix_promo_ariary__gte=models.F('prix_ariary'))
        )