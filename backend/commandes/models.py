from django.db import models
from utilisateurs.models import Utilisateur
from produits.models import Produit
from services.models import ServiceIT


class Commande(models.Model):
    STATUT = [
        ('envoyee', 'Envoyée sur WhatsApp'),
        ('en_cours', 'En cours de traitement'),
        ('validee', 'Validée'),
        ('annulee', 'Annulée'),
    ]
    client = models.ForeignKey(Utilisateur, on_delete=models.PROTECT, related_name='commandes')
    total_ariary = models.DecimalField(max_digits=12, decimal_places=2)
    statut = models.CharField(max_length=10, choices=STATUT, default='envoyee')
    message_whatsapp = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commande #{self.id}- Client #{self.client} - {self.total_ariary} Ar"

class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.SET_NULL, null=True, blank=True)
    service = models.ForeignKey(ServiceIT, on_delete=models.SET_NULL, null=True, blank=True)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2)