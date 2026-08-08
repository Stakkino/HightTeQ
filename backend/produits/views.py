from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q

from .models import Marque, Categorie, Produit, ImageProduit, AvisProduit
from .serializers import (
    MarqueSerializer,
    CategorieSerializer,
    ProduitListeSerializer,
    ProduitDetailSerializer,
    ProduitCreateUpdateSerializer,
    AvisProduitSerializer,
    ImageProduitSerializer
)
from .filters import ProduitFilter
from .permissions import EstAdminOuLectureSeule
from .pagination import ProduitPagination


class MarqueViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint pour les marques (lecture seule)
    
    Endpoints:
    - GET /api/marques/ : Liste toutes les marques
    - GET /api/marques/{id}/ : Détail d'une marque
    """
    queryset = Marque.objects.all()
    serializer_class = MarqueSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'description']
    ordering_fields = ['nom', 'date_creation']
    
    @action(detail=True, methods=['get'])
    def produits(self, request, pk=None):
        """GET /api/marques/{id}/produits/ : Produits d'une marque"""
        marque = self.get_object()
        produits = Produit.objects.filter(marque=marque, est_actif=True)
        page = self.paginate_queryset(produits)
        if page is not None:
            serializer = ProduitListeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProduitListeSerializer(produits, many=True)
        return Response(serializer.data)


class CategorieViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint pour les catégories (lecture seule)
    
    Endpoints:
    - GET /api/categories/ : Liste toutes les catégories
    - GET /api/categories/{slug}/ : Détail d'une catégorie
    """
    queryset = Categorie.objects.filter(est_active=True).prefetch_related('sous_categories')
    serializer_class = CategorieSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['nom', 'description']
    
    @action(detail=True, methods=['get'])
    def produits(self, request, slug=None):
        """GET /api/categories/{slug}/produits/ : Produits d'une catégorie"""
        categorie = self.get_object()
        # Inclure les sous-catégories
        categories = [categorie]
        sous_categories = categorie.sous_categories.all()
        categories.extend(sous_categories)
        
        produits = Produit.objects.filter(
            categorie__in=categories,
            est_actif=True
        ).distinct()
        
        page = self.paginate_queryset(produits)
        if page is not None:
            serializer = ProduitListeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProduitListeSerializer(produits, many=True)
        return Response(serializer.data)


class ProduitViewSet(viewsets.ModelViewSet):
    """
    API endpoint pour les produits
    
    Endpoints publics:
    - GET /api/produits/ : Liste paginée avec filtres
    - GET /api/produits/{slug}/ : Détail d'un produit
    
    Endpoints admin (nécessite authentification staff):
    - POST /api/produits/ : Créer un produit
    - PUT/PATCH /api/produits/{slug}/ : Modifier un produit
    - DELETE /api/produits/{slug}/ : Supprimer un produit
    
    Actions spéciales:
    - GET /api/produits/en_vedette/ : Produits en vedette
    - GET /api/produits/promotions/ : Produits en promotion
    - GET /api/produits/{slug}/avis/ : Avis d'un produit
    - POST /api/produits/{slug}/ajouter_avis/ : Ajouter un avis
    """
    queryset = Produit.objects.filter(est_actif=True).select_related('marque', 'categorie')
    permission_classes = [EstAdminOuLectureSeule]
    pagination_class = ProduitPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProduitFilter
    search_fields = ['nom', 'description', 'marque__nom']
    ordering_fields = ['prix_ariary', 'date_creation', 'nom', 'stock']
    ordering = ['-date_creation']  # Tri par défaut
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        """Retourne le sérialiseur approprié selon l'action"""
        if self.action == 'list':
            return ProduitListeSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProduitCreateUpdateSerializer
        return ProduitDetailSerializer
    
    def get_permissions(self):
        """Permissions spéciales pour l'ajout d'avis"""
        if self.action == 'ajouter_avis':
            return [IsAuthenticatedOrReadOnly()]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'])
    def en_vedette(self, request):
        """GET /api/produits/en_vedette/ : Produits mis en avant"""
        produits = self.queryset.filter(est_en_vedette=True)[:8]
        serializer = ProduitListeSerializer(produits, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def promotions(self, request):
        """GET /api/produits/promotions/ : Produits en promotion"""
        produits = self.queryset.filter(
            prix_promo_ariary__isnull=False,
            prix_promo_ariary__lt=models.F('prix_ariary')
        )[:20]
        serializer = ProduitListeSerializer(produits, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def nouveautes(self, request):
        """GET /api/produits/nouveautes/ : Nouveaux produits"""
        produits = self.queryset.filter(badge='nouveau').order_by('-date_creation')[:12]
        serializer = ProduitListeSerializer(produits, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def avis(self, request, slug=None):
        """GET /api/produits/{slug}/avis/ : Avis d'un produit"""
        produit = self.get_object()
        avis = produit.avis.filter(est_approuve=True)
        serializer = AvisProduitSerializer(avis, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def ajouter_avis(self, request, slug=None):
        """POST /api/produits/{slug}/ajouter_avis/ : Ajouter un avis"""
        produit = self.get_object()
        
        # Vérifier si l'utilisateur a déjà donné son avis
        if request.user.is_authenticated:
            avis_existant = AvisProduit.objects.filter(
                produit=produit,
                email_client=request.user.email
            ).exists()
            
            if avis_existant:
                return Response(
                    {'detail': 'Vous avez déjà donné votre avis sur ce produit'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = AvisProduitSerializer(
            data=request.data,
            context={'produit_id': produit.id}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def similaires(self, request, slug=None):
        """GET /api/produits/{slug}/similaires/ : Produits similaires"""
        produit = self.get_object()
        similaires = Produit.objects.filter(
            categorie=produit.categorie,
            est_actif=True
        ).exclude(id=produit.id)[:6]
        serializer = ProduitListeSerializer(similaires, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """GET /api/produits/stats/ : Statistiques des produits (admin)"""
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        from django.db.models import Avg, Sum
        
        stats = {
            'total_produits': Produit.objects.count(),
            'produits_actifs': Produit.objects.filter(est_actif=True).count(),
            'en_promotion': Produit.objects.filter(
                prix_promo_ariary__isnull=False,
                prix_promo_ariary__lt=models.F('prix_ariary')
            ).count(),
            'rupture_stock': Produit.objects.filter(stock=0).count(),
            'stock_faible': Produit.objects.filter(stock__lte=5, stock__gt=0).count(),
            'prix_moyen': Produit.objects.aggregate(Avg('prix_ariary'))['prix_ariary__avg'],
            'categories': Categorie.objects.count(),
            'marques': Marque.objects.count(),
        }
        return Response(stats)