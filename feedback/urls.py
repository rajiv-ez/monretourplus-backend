from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AvisViewSet, ReclamationViewSet,
    CategorieReclamationViewSet, ServiceViewSet, ClientViewSet,
    ClientMeView, ReclamationFullViewSet, AvisFullViewSet
)

router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'avis/full', AvisFullViewSet, basename='avis_full')
router.register(r'avis', AvisViewSet, basename='avis')
router.register(r'reclamations/full', ReclamationFullViewSet, basename='reclamations_full')
router.register(r'reclamations', ReclamationViewSet, basename='reclamations')
router.register(r'services', ServiceViewSet)
router.register(r'categories-reclamations', CategorieReclamationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('client/me/', ClientMeView.as_view(), name='client_me'),
]