from rest_framework import serializers
from .models import ServiceIT

class ServiceITSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceIT
        fields = ['id', 'nom', 'description', 'type_tarif', 'tarif', 'delai_intervention']