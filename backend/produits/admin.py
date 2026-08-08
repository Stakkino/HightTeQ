from django.contrib import admin
from django.utils.html import format_html
from .models import Marque, Categorie, Produit, ImageProduit, AvisProduit


class ImageProduitInline(admin.TabularInline):
    model = ImageProduit
    extra = 1
    fields = ['image', 'legende', 'ordre']


class AvisProduitInline(admin.TabularInline):
    model = AvisProduit
    extra = 0
    readonly_fields = ['date_creation']
    fields = ['nom_client', 'email_client', 'note', 'commentaire', 'est_approuve']


@admin.register(Marque)
class MarqueAdmin(admin.ModelAdmin):
    list_display = ['nom', 'logo_preview', 'site_web', 'date_creation']
    search_fields = ['nom']
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.logo.url)
        return "-"
    logo_preview.short_description = "Aperçu logo"


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'slug', 'parent', 'est_active', 'ordre']
    list_filter = ['est_active', 'parent']
    search_fields = ['nom']
    prepopulated_fields = {'slug': ('nom',)}
    list_editable = ['ordre', 'est_active']


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'nom', 'categorie', 'marque', 'prix_ariary', 'prix_actuel_display', 'stock_status', 'badge', 'est_actif', 'est_en_vedette']  # ← Ajouté ici
    list_filter = ['categorie', 'marque', 'badge', 'est_actif', 'est_en_vedette', 'date_creation']
    search_fields = ['nom', 'description', 'marque__nom']
    prepopulated_fields = {'slug': ('nom',)}
    list_editable = ['est_actif', 'est_en_vedette']
    inlines = [ImageProduitInline, AvisProduitInline]
    readonly_fields = ['date_creation', 'date_modification', 'prix_actuel_display']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('nom', 'slug', 'categorie', 'marque', 'description')
        }),
        ('Prix', {
            'fields': ('prix_ariary', 'prix_promo_ariary', 'prix_actuel_display')
        }),
        ('Stock et État', {
            'fields': ('stock', 'est_actif', 'est_en_vedette', 'badge')
        }),
        ('Médias', {
            'fields': ('image',)
        }),
        ('Détails supplémentaires', {
            'fields': ('caracteristiques', 'poids_kg'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 40px;"/>', obj.image.url)
        return "Pas d'image"
    image_preview.short_description = "Image"
    
    def prix_actuel_display(self, obj):
        if obj.en_promotion:
            return format_html(
                '<span style="text-decoration: line-through; color: red;">{} Ar</span> '
                '<span style="color: green; font-weight: bold;">{} Ar</span>',
                obj.prix_ariary, obj.prix_actuel
            )
        return f"{obj.prix_ariary} Ar"
    prix_actuel_display.short_description = "Prix actuel"
    
    def stock_status(self, obj):
        if obj.stock == 0:
            return format_html('<span style="color: red;">❌ Rupture</span>')
        elif obj.stock < 5:
            return format_html('<span style="color: orange;">⚠️ {} restant(s)</span>', obj.stock)
        return format_html('<span style="color: green;">✅ {} en stock</span>', obj.stock)
    stock_status.short_description = "Stock"


@admin.register(AvisProduit)
class AvisProduitAdmin(admin.ModelAdmin):
    list_display = ['produit', 'nom_client', 'note_stars', 'est_approuve', 'date_creation']
    list_filter = ['est_approuve', 'note', 'date_creation']
    search_fields = ['nom_client', 'commentaire', 'produit__nom']
    list_editable = ['est_approuve']
    
    def note_stars(self, obj):
        stars = '⭐' * obj.note
        return format_html('<span style="color: gold;">{}</span>', stars)
    note_stars.short_description = "Note"