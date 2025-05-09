from rest_framework import serializers
from .models import Avis, Reclamation, Client, Service
from .models import Client
from accounts.serializers import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    
    class Meta:
        model = Client
        fields = '__all__'

    def create(self, validated_data):
        user_data = validated_data.pop("user", None)
        if user_data:
            user = User.objects.create_user(
                username=user_data["username"],
                email=user_data.get("email"),
                password=user_data.get("password", "defaultpass")  # peut être changé
            )
            validated_data["user"] = user
        return Client.objects.create(**validated_data)


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'




class AvisSerializer(serializers.ModelSerializer):
    service_concerne = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), write_only=True)
    service_concerne_detail = ServiceSerializer(source="service_concerne", read_only=True)

    class Meta:
        model = Avis
        fields = ['id', 'client', 'note', 'commentaire', 'service_concerne', 'service_concerne_detail', 'nom_structure', 'nom', 'prenom', 'email', 'telephone',  'date_submitted']


class ReclamationSerializer(serializers.ModelSerializer):
    service_concerne = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), write_only=True)
    service_concerne_detail = ServiceSerializer(source="service_concerne", read_only=True)

    class Meta:
        model = Reclamation
        fields = ['id', 'client', 'sujet', 'description',  'service_concerne', 'service_concerne_detail', 'nom_structure', 'nom', 'prenom', 'email', 'telephone', 'booking_number', 'numero_suivi', 'statut', 'date_submitted']


