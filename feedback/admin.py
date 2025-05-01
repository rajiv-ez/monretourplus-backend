from django.contrib import admin
from.models import Avis, Reclamation, Client, CategorieReclamation, Service

# Register your models here.
admin.site.register(Avis)
admin.site.register(Client)
admin.site.register(Reclamation)
admin.site.register(Service)
admin.site.register(CategorieReclamation)