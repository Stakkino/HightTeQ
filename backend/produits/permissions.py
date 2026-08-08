from rest_framework import permissions


class EstAdminOuLectureSeule(permissions.BasePermission):
    """
    Permission personnalisée :
    - Tout le monde peut lire (GET, HEAD, OPTIONS)
    - Seuls les admins peuvent écrire (POST, PUT, PATCH, DELETE)
    """
    
    def has_permission(self, request, view):
        # Autoriser les méthodes de lecture pour tout le monde
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Autoriser l'écriture uniquement pour les admins
        return request.user and request.user.is_staff


class EstAuteurOuAdmin(permissions.BasePermission):
    """
    Permission pour les avis :
    - L'auteur peut modifier son avis
    - Les admins peuvent tout faire
    """
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user.is_staff or obj.email_client == request.user.email