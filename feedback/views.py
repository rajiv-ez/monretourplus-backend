from django.shortcuts import render
from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from .models import Avis, Reclamation, Service, Client
from .serializers import AvisSerializer, ReclamationSerializer, ClientSerializer, ServiceSerializer
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from mytools.email import send_notification_email
from django.template.loader import render_to_string

User = get_user_model()

def test(request):
    return render(request, "emails/statut_reclamation.html", {
        "reclamation":{
            "nom_structure":"EZ Audiovisuel",
            "nom":"NKOMO ELLA",
            "prenom":"Rajiv",
            "email":"nkomoellarajiv.pro@gmail.com",
            "telephone":"074676038",
            "service_concerne":"Accueil",
            "sujet":"Arnaque",
            "description":"Il m'en a demandé plus que nécessaire",
            "booking_number": "E1AZTY",
            "numero_suivi": "DKFKIEEPPEKF8348940",
            "statut": "En attente",

        }
    })

class AvisViewSet(viewsets.ModelViewSet):
    """Vue pour gérer les avis des clients."""
    queryset = Avis.objects.all()
    serializer_class = AvisSerializer
    permission_classes = [permissions.AllowAny]
    #permission_classes = [permissions.IsAuthenticated]

    # def get_queryset(self):
    #     client_user_id = self.request.query_params.get("client")
    #     if client_user_id:
    #         return Avis.objects.filter(client__user__id=client_user_id)
    #     return Avis.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        avis = serializer.save()

        email_destinataire = avis.email.strip() if avis.email else None
        if not email_destinataire:
            return Response({"error": "Adresse email manquante ou invalide."}, status=400)
        
        # Email au service commercial
        message_html = render_to_string("emails/notification_nouvel_avis.html", {"avis": avis})

        send_notification_email(
            "💬 Merci pour votre avis sur MonRetourMSC+", 
            "", 
            None,
            message_html
        )

        # Accusée réception au client
        message2_html = render_to_string("emails/acknowledgment_avis.html", {"avis": avis})

        send_notification_email(
            f"⚠ Nouvel avis - { avis.note } étoiles", 
            "", 
            [email_destinataire],
            message2_html
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ReclamationViewSet(viewsets.ModelViewSet):
    """Vue pour gérer les réclamations des clients."""
    queryset = Reclamation.objects.all()
    serializer_class = ReclamationSerializer
    permission_classes = [permissions.AllowAny]
    # permission_classes = [permissions.IsAuthenticated]

    # def get_queryset(self):
    #     if self.request.user.is_staff or self.request.user.is_superuser or self.request.user.is_admin:
    #         return Reclamation.objects.all()
    #     client_user_id = self.request.query_params.get("client")
    #     if client_user_id:
    #         return Reclamation.objects.filter(client__user__id=client_user_id)
    #     return Reclamation.objects.none()

    
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

            
            # Préparation de l'email
            email_destinataire = instance.email.strip() if instance.email else None
            if not email_destinataire:
                return Response({"error": "Adresse email manquante ou invalide."}, status=400)

            if new_status == "inProgress":
                subject = f"📍 Votre réclamation est en cours de résolution - {instance.numero_suivi}"
            elif new_status == "resolved":
                subject = f"✅ Votre réclamation a été résolue - {instance.numero_suivi}"
            template_name = "emails/statut_reclamation.html"

            # Rendu HTML
            message_html = render_to_string(template_name, {"reclamation": instance})

            send_notification_email(
                subject, 
                "", 
                [email_destinataire],
                message_html
            )

            return Response({"success": "Statut mis à jour"}, status=200)
        except Reclamation.DoesNotExist:
            return Response({"error": "Réclamation introuvable"}, status=404)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reclamation = serializer.save()

        email_destinataire = reclamation.email.strip() if reclamation.email else None
        if not email_destinataire:
            return Response({"error": "Adresse email manquante ou invalide."}, status=400)

        
        message_html = render_to_string("emails/notification_nouvelle_reclamation.html", {"reclamation": reclamation})

        send_notification_email(
            f"⚠ Nouvelle réclamation - ID: {reclamation.numero_suivi}", 
            "", 
            None,
            message_html
        )

        # Accusée réception au client
        message2_html = render_to_string("emails/acknowledgment_reclamation.html", {"reclamation": reclamation})

        send_notification_email(
            f"💬 Votre réclamation {reclamation.numero_suivi} sur MonRetourMSC+", 
            "", 
            [email_destinataire],
            message2_html
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)










class AvisFullViewSet(viewsets.ModelViewSet):
    """Vue pour gérer les catégories de réclamations."""
    queryset = Avis.objects.all()
    serializer_class = AvisSerializer

class ReclamationFullViewSet(viewsets.ModelViewSet):
    """Vue pour gérer les catégories de réclamations."""
    queryset = Reclamation.objects.all()
    serializer_class = ReclamationSerializer


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


class ClientFullProfileView(APIView):
    """
    Vue API qui retourne le profil complet du client connecté,
    y compris ses réclamations et ses avis.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            client = Client.objects.get(user=request.user)
        except Client.DoesNotExist:
            return Response({"detail": "Client non trouvé."}, status=status.HTTP_404_NOT_FOUND)

        reclamations = Reclamation.objects.filter(client=client)
        avis = Avis.objects.filter(client=client)

        return Response({
            "client": ClientSerializer(client).data,
            "reclamations": ReclamationSerializer(reclamations, many=True).data,
            "avis": AvisSerializer(avis, many=True).data
        })

class UpdateClientProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        client = Client.objects.filter(user=request.user).first()
        data = request.data

        client.nom = data.get('nom', client.nom)
        client.prenom = data.get('prenom', client.prenom)
        client.email = data.get('email', client.email)
        client.nom_structure = data.get('nom_structure', client.nom_structure)
        client.telephone = data.get('telephone', client.telephone)
        client.save()

        return Response({
            'status': 'success',
            'nom': client.nom,
            'prenom': client.prenom,
            'email': client.email,
            'nom_structure': client.nom_structure,
            'telephone': client.telephone,
        })

  