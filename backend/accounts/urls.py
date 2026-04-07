from django.urls import path
from . import views

urlpatterns = [
    path('auth/csrf/', views.csrf_view),
    path('auth/register/', views.register_view),
    path('auth/login/', views.login_view),
    path('auth/logout/', views.logout_view),
    path('auth/me/', views.me_view),
    path('profile/', views.profile_view),
    path('profile/delete/', views.delete_account_view),
    path('dashboard/', views.dashboard_view),
    path('admin/overview/', views.admin_overview),
    path('admin/users/', views.admin_users),
    path('admin/users/<uuid:uid>/', views.admin_user_detail),
]
