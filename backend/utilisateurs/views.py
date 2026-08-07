from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Utilisateur
from .serializers import InscriptionSerializer, UtilisateurSerializer

class InscriptionView(generics.CreateAPIView):
    """POST /api/utilisateurs/inscription/ — ouvert à tout le monde."""
    queryset = Utilisateur.objects.all()
    serializer_class = InscriptionSerializer
    permission_classes = [permissions.AllowAny]

class ProfilView(generics.RetrieveUpdateAPIView):
    """GET/PUT /api/utilisateurs/profil/ — l'utilisateur connecté consulte/modifie ses infos."""
    serializer_class = UtilisateurSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class ConnexionView(TokenObtainPairView):
    """POST /api/utilisateurs/connexion/ — renvoie access + refresh token JWT."""
    pass
