from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (test,
    AvisViewSet, ReclamationViewSet,
    ServiceViewSet, ClientViewSet,
    ClientMeView, ReclamationFullViewSet, AvisFullViewSet,
    ClientFullProfileView, UpdateClientProfileView,
)

router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'avis/full', AvisFullViewSet, basename='avis_full')
router.register(r'avis', AvisViewSet, basename='avis')
router.register(r'reclamations/full', ReclamationFullViewSet, basename='reclamations_full')
router.register(r'reclamations', ReclamationViewSet, basename='reclamations')
router.register(r'services', ServiceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('test', test, name="test"),
    path('client/me/', ClientMeView.as_view(), name='client_me'),
    path('client/full-profile/', ClientFullProfileView.as_view(), name='client-full-profile'),
    path('client/update-profile/', UpdateClientProfileView.as_view(), name='client-full-profile-update'),
]