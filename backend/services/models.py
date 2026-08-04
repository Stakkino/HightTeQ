from django.db import models

class ServiceIT(models.Model):
    listetarif=[
        ('forfait', 'Forfait fixe'),
        ('horaire', 'Tarif horaire'),
        ('devis', 'Sur devis'),
    ]
    nom = models.CharField(max_length=200)
    description = models.TextField()
    type_tarif = models.CharField(max_length=20, choices=listetarif)
    tarif = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    delai_intervention = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nom
