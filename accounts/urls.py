from django.urls import path
from .views import RegisterView, CustomTokenView, ChangePasswordView, AdminUserListView, ChangeOtherUserPasswordView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='auth_register'),
    path('api/login/', CustomTokenView.as_view(), name='token_obtain_pair'),
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path("api/change-password/<int:user_id>/", ChangeOtherUserPasswordView.as_view(), name="change-user-password"),
    path('api/users/', AdminUserListView.as_view(), name='admin-user-list'),
]