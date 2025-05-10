from django.contrib import admin
from django.urls import path, include
from .views import ReactAppView

from django.views.generic import TemplateView
from django.views.static import serve
from django.conf import settings
from django.urls import re_path

urlpatterns = [
    path('manage/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('api/', include('feedback.urls')),
    path("", ReactAppView.as_view(), name="home"),  # catch-all pour React
]

# Sert React index.html pour toute URL non API/admin
urlpatterns += [
    re_path(r"^(?!api|manage|accounts|static).*", TemplateView.as_view(template_name="index.html"), name="index"),
]
