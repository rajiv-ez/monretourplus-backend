from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

# Va sauter
class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    nom_structure = models.CharField(max_length=255)
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    email = models.EmailField()
    telephone = models.CharField(max_length=20, null=True)

    def __str__(self):
        return f"{self.nom_structure} - {self.nom} {self.prenom}"
# Fin va sauter
    
class Service(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.nom

class Avis(models.Model):
    NOTE_CHOICES = [(i, str(i)) for i in range(1, 6)]

    #client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)

    # nom_structure = models.CharField(max_length=255)
    # nom = models.CharField(max_length=255)
    # prenom = models.CharField(max_length=255, null=True)
    # telephone = models.CharField(max_length=20, null=True)

    email = models.EmailField(null=True, blank=True)
    
    service_concerne = models.ForeignKey(Service, on_delete=models.CASCADE, null=True)
    note = models.IntegerField(choices=NOTE_CHOICES)
    commentaire = models.TextField(blank=True) # En cas d'avis negatif, le champ deviens obligatoire pour permettre au transitaire d’expliquer les raisons de son insatisfaction.
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        formated_date = self.date_submitted.strftime("%d/%m/%Y, %H:%M:%S")
        return f"Avis du {formated_date} de {self.prenom} {self.nom}"

class Reclamation(models.Model):
    STATUTS = [
        ("pending", "En attente"),
        ("inProgress", "En cours"),
        ("rejected", "Rejetée"),
        ("resolved", "Résolue"),
    ]

    # client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    
    # nom_structure = models.CharField(max_length=255)
    # nom = models.CharField(max_length=255)
    # prenom = models.CharField(max_length=255, null=True)
    # telephone = models.CharField(max_length=20)
    
    email = models.EmailField(null=True, blank=True)
    
    description = models.TextField()
    service_concerne = models.ForeignKey(Service, on_delete=models.CASCADE, null=True)
    sujet = models.CharField(max_length=255)

    booking_number = models.CharField(max_length=100, null=True)
    numero_suivi = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    statut = models.CharField(max_length=50, choices=STATUTS, default="pending")
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Réclamation #{self.numero_suivi} de {self.prenom} {self.nom}"
