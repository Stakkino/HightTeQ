from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator

class Marque(models.Model):
    nom = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='marques/', blank=True, null=True)
    description = models.TextField(blank=True)
    site_web = models.URLField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Marque"
        verbose_name_plural = "Marques"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sous_categories')
    ordre = models.IntegerField(default=0)
    est_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['ordre', 'nom']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nom


class Produit(models.Model):
    # Choix pour le badge
    BADGE_CHOICES = [
        ('nouveau', 'Nouveau'),
        ('promo', 'En Promotion'),
        ('epuise', 'Épuisé'),
        ('bestseller', 'Meilleure Vente'),
        ('precommande', 'Précommande'),
    ]
    
    nom = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    marque = models.ForeignKey(Marque, on_delete=models.SET_NULL, null=True, blank=True, related_name='produits')
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='produits')  # Correction: minuscule
    description = models.TextField()
    caracteristiques = models.TextField(blank=True, help_text="Caractéristiques techniques du produit")
    prix_ariary = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    prix_promo_ariary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='produits/', blank=True, null=True)
    badge = models.CharField(max_length=50, choices=BADGE_CHOICES, blank=True, null=True)
    est_actif = models.BooleanField(default=True, verbose_name="Produit actif")
    est_en_vedette = models.BooleanField(default=False, verbose_name="Mettre en vedette")
    poids_kg = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, help_text="Poids en kilogrammes")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['categorie', 'est_actif']),
            models.Index(fields=['marque']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nom)
            slug = base_slug
            compteur = 1
            while Produit.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{compteur}"
                compteur += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nom
    
    @property
    def prix_actuel(self):
        """Retourne le prix promotionnel s'il existe, sinon le prix normal"""
        if self.prix_promo_ariary and self.prix_promo_ariary < self.prix_ariary:
            return self.prix_promo_ariary
        return self.prix_ariary
    
    @property
    def en_promotion(self):
        """Vérifie si le produit est en promotion"""
        return self.prix_promo_ariary is not None and self.prix_promo_ariary < self.prix_ariary
    
    @property
    def pourcentage_reduction(self):
        """Calcule le pourcentage de réduction"""
        if self.en_promotion:
            reduction = ((self.prix_ariary - self.prix_promo_ariary) / self.prix_ariary) * 100
            return round(reduction)
        return 0
    
    @property
    def est_disponible(self):
        """Vérifie si le produit est en stock"""
        return self.stock > 0 and self.est_actif


class ImageProduit(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='produits/galerie/')
    legende = models.CharField(max_length=200, blank=True)
    ordre = models.IntegerField(default=0)
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Image du produit"
        verbose_name_plural = "Images du produit"
        ordering = ['ordre']
    
    def __str__(self):
        return f"Image {self.ordre} - {self.produit.nom}"


class AvisProduit(models.Model):
    NOTE_CHOICES = [(i, f"{i} étoile(s)") for i in range(1, 6)]
    
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='avis')
    nom_client = models.CharField(max_length=100)
    email_client = models.EmailField()
    note = models.IntegerField(choices=NOTE_CHOICES)
    commentaire = models.TextField()
    est_approuve = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Avis produit"
        verbose_name_plural = "Avis produits"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Avis de {self.nom_client} - {self.note}/5"