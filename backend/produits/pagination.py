from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ProduitPagination(PageNumberPagination):
    """Pagination personnalisée pour les produits"""
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'total_produits': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'page_actuelle': self.page.number,
            'page_suivante': self.get_next_link(),
            'page_precedente': self.get_previous_link(),
            'resultats': data
        })