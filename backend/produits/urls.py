from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'marques', views.MarqueViewSet, basename='marque')
router.register(r'categories', views.CategorieViewSet, basename='categorie')
router.register(r'produits', views.ProduitViewSet, basename='produit')

app_name = 'produits'

urlpatterns = [
    path('', include(router.urls)),
]