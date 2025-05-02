from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from .models import Avis, Reclamation, CategorieReclamation, Service, Client
from .serializers import AvisSerializer, ReclamationSerializer, ClientSerializer, ServiceSerializer, CategorieReclamationSerializer
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from mytools.email import send_notification_email

User = get_user_model()

class AvisViewSet(viewsets.ModelViewSet):
    """Vue pour gérer les avis des clients."""
    serializer_class = AvisSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        client_user_id = self.request.query_params.get("client")
        if client_user_id:
            return Avis.objects.filter(client__user__id=client_user_id)
        return Avis.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        avis = serializer.save()

        sujet =  f"⚠ Nouvel avis - { avis.note } étoiles"
        message = f"""
        Client : { avis.nom } { avis.prenom }
        Structure : {avis.nom_structure }
        Numéro de reservation : {avis.booking_number }
        Service concerné : { avis.service_concerne }
        Commentaire : { avis.commentaire }
        Note : { avis.note } étoiles
        Email : { avis.email }
        Téléphone : { avis.telephone }    
        """
        send_notification_email(sujet, message, None)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Email au service commercial
        # subject = " Nouvel avis client reçu"
        # message = render_to_string("emails/nouvel_avis.html", {"avis": avis})
        # email = EmailMultiAlternatives(subject, message, to=["nkomoellarajiv.pro@gmail.com"])
        # email.attach_alternative(message, "text/html")
        # email.send()

        # # Accusé de réception client
        # subject_client = " Votre avis a bien été reçu"
        # message_client = render_to_string("emails/accuse_avis.html", {"avis": avis})
        # email_client = EmailMultiAlternatives(subject_client, message_client, to=[avis.email])
        # email_client.attach_alternative(message_client, "text/html")
        # email_client.send()

class ReclamationViewSet(viewsets.ModelViewSet):
    """Vue pour gérer les réclamations des clients."""
    serializer_class = ReclamationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser or self.request.user.is_admin:
            return Reclamation.objects.all()
        
        client_user_id = self.request.query_params.get("client")
        if client_user_id:
            return Reclamation.objects.filter(client__user__id=client_user_id)
        
        return Reclamation.objects.none()

    
    @action(detail=True, methods=["patch"], permission_classes=[IsAdminUser])
    def statut(self, request, pk=None):
        print("request.data", request.data)
        try:
            instance = self.get_object()
            new_status = request.data.get("statut")
            if new_status not in ["pending", "inProgress", "resolved"]:
                return Response({"error": "Statut invalide"}, status=400)

            instance.statut = new_status
            instance.save()
            return Response({"success": "Statut mis à jour"}, status=200)
        except Reclamation.DoesNotExist:
            return Response({"error": "Réclamation introuvable"}, status=404)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reclamation = serializer.save()

        sujet =  f"⚠ Nouvelle réclamation - ID: { reclamation.numero_suivi }"
        message = f"""
        Client : { reclamation.nom } { reclamation.prenom }
        Structure : {reclamation.nom_structure }
        Numéro de reservation : {reclamation.booking_number }
        Catégorie : { reclamation.categorie }
        Sujet : { reclamation.sujet }
        Description : { reclamation.description }
        Email : { reclamation.email }
        Téléphone : { reclamation.telephone }   

        Statut : { reclamation.statut }    
        """

        # reclamation = self.get_queryset().get(id=response.data["id"])
        # send_notification_email(reclamation)

        send_notification_email(sujet, message, None)
        return Response(serializer.data, status=status.HTTP_201_CREATED)










class AvisFullViewSet(viewsets.ModelViewSet):
    """Vue pour gérer les catégories de réclamations."""
    queryset = Avis.objects.all()
    serializer_class = AvisSerializer

class ReclamationFullViewSet(viewsets.ModelViewSet):
    """Vue pour gérer les catégories de réclamations."""
    queryset = Reclamation.objects.all()
    serializer_class = ReclamationSerializer


class CategorieReclamationViewSet(viewsets.ModelViewSet):
    """Vue pour gérer les catégories de réclamations."""
    queryset = CategorieReclamation.objects.all().order_by('nom')
    serializer_class = CategorieReclamationSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    """Vue pour gérer les services."""
    queryset = Service.objects.all().order_by('nom')
    serializer_class = ServiceSerializer

class ClientViewSet(viewsets.ModelViewSet):
    """Vue pour gérer les clients."""
    queryset = Client.objects.all().order_by('nom')
    serializer_class = ClientSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]








class ClientMeView2(APIView):
    """Vue pour gérer les informations du client connecté."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            client = Client.objects.get(user=request.user)
            return Response(ClientSerializer(client).data)
        except Client.DoesNotExist:
            return Response({"detail": "Client non trouvé."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        try:
            client = Client.objects.get(user=request.user)
            serializer = ClientSerializer(client, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Client.DoesNotExist:
            return Response({"detail": "Client non trouvé."}, status=status.HTTP_404_NOT_FOUND)
    




class ClientMeView3(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        client_id = request.query_params.get("client_id")
        if not client_id:
            return Response({"detail": "client_id requis"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            client = Client.objects.get(id=client_id)
            return Response(ClientSerializer(client).data)
        except Client.DoesNotExist:
            return Response({"detail": "Client non trouvé."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        client_id = request.data.get("id")
        try:
            client = Client.objects.get(id=client_id)
            serializer = ClientSerializer(client, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Client.DoesNotExist:
            return Response({"detail": "Client non trouvé."}, status=status.HTTP_404_NOT_FOUND)





class ClientMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Retourne les informations du client lié à l'utilisateur connecté."""
        try:
            client = Client.objects.get(user=request.user)
            return Response(ClientSerializer(client).data)
        except Client.DoesNotExist:
            return Response({"detail": "Client non trouvé."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        """Mise à jour des informations du client connecté."""
        try:
            client = Client.objects.get(user=request.user)
            serializer = ClientSerializer(client, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Client.DoesNotExist:
            return Response({"detail": "Client non trouvé."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """Retourne les informations du client en utilisant user_id transmis explicitement."""
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"detail": "user_id manquant"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            client = Client.objects.get(user__id=user_id)
            return Response(ClientSerializer(client).data)
        except Client.DoesNotExist:
            return Response({"detail": "Client non trouvé."}, status=status.HTTP_404_NOT_FOUND)
