from django.contrib import admin
from .models import Commande, LigneCommande

class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'total_ariary', 'statut', 'date_creation')
    list_filter = ('statut',)
    inlines = [LigneCommandeInline]
