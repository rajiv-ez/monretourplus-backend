from rest_framework import generics, permissions, status
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

User = get_user_model()

class AdminUserListView(generics.ListAPIView):
    queryset = User.objects.filter(is_admin=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class RegisterView(generics.CreateAPIView):
    """View for user registration."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class CustomTokenView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ChangePasswordView(APIView):
    """Vue pour changer le mot de passe de l'utilisateur connecté."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        current = request.data.get("current_password")
        new = request.data.get("new_password")

        if not user.check_password(current):
            return Response({"error": "Mot de passe actuel invalide."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new)
        user.save()
        return Response({"success": "Mot de passe mis à jour."})

from rest_framework.generics import get_object_or_404
from django.contrib.auth import get_user_model

class ChangeOtherUserPasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        if not request.user.is_admin:
            return Response({"error": "Non autorisé."}, status=status.HTTP_403_FORBIDDEN)
        
        new_password = request.data.get("new_password")
        if not new_password:
            return Response({"error": "Mot de passe requis."}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(get_user_model(), id=user_id)
        user.set_password(new_password)
        user.save()
        return Response({"success": "Mot de passe modifié."})




