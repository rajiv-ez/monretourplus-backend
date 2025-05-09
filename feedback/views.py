from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from .models import Avis, Reclamation,  Service, Client
from .serializers import AvisSerializer, ReclamationSerializer, ClientSerializer, ServiceSerializer
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from mytools.email import send_notification_email
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


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

        email_destinataire = avis.email.strip() if avis.email else None
        if not email_destinataire:
            return Response({"error": "Adresse email manquante ou invalide."}, status=400)

        # Sujet de l'email
        subject = "💬 Merci pour votre avis sur MonRetourMSC+"

        # Rendu HTML
        message_html = render_to_string("emails/nouvel_avis.html", {"avis": avis})

        # Envoi de l'email
        email = EmailMultiAlternatives(
            subject=subject,
            body=message_html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_destinataire],
        )
        email.attach_alternative(message_html, "text/html")
        email.send(fail_silently=False)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    


class ReclamationViewSet(viewsets.ModelViewSet):
    """Vue pour gérer les réclamations des clients."""
    serializer_class = ReclamationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if getattr(user, 'is_admin', False) or user.is_staff or user.is_superuser:
            return Reclamation.objects.all()
        client_user_id = self.request.query_params.get("client")
        if client_user_id:
            return Reclamation.objects.filter(client__user__id=client_user_id)
        
        return Reclamation.objects.none()


   

    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated])
    def statut(self, request, pk=None):

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

            email = EmailMultiAlternatives(
                subject=subject,
                body=message_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email_destinataire],
            )
            email.attach_alternative(message_html, "text/html")
            email.send(fail_silently=False)

            return Response({"success": "Statut mis à jour et email envoyé"}, status=200)

        except Reclamation.DoesNotExist:
            return Response({"error": "Réclamation introuvable"}, status=404)


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reclamation = serializer.save()
        email_destinataire = reclamation.email.strip() if reclamation.email else None

        if not email_destinataire:
            return Response({"error": "Adresse email manquante ou invalide."}, status=status.HTTP_400_BAD_REQUEST)

        # Sujet de l'email
        sujet = f"⚠ Nouvelle réclamation - ID: {reclamation.numero_suivi}"

        # Rendre le template HTML avec les données de la réclamation
        message_html = render_to_string("emails/nouvelle_reclamation.html", {"reclamation": reclamation})

        # Créer l'email en texte brut et HTML
        email = EmailMultiAlternatives(
            subject=sujet,
            body=message_html,  # Corps de l'email en texte brut
            from_email=settings.DEFAULT_FROM_EMAIL,  # Définir l'email d'expéditeur
            to=[reclamation.email],  # Envoi à l'email du client qui a fait la réclamation
        )
        
        # Ajouter la version HTML
        email.attach_alternative(message_html, "text/html")

        # Envoyer l'email
        email.send(fail_silently=False)

        # Retourner la réponse API
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

    