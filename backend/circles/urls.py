from django.urls import path
from . import views

urlpatterns = [
    path('circles/', views.circles_list_create),
    path('circles/mine/', views.my_circles),
    path('circles/active/', views.active_circle),
    path('circles/<uuid:pk>/', views.circle_detail),
    path('circles/<uuid:pk>/members/', views.circle_members),
    path('circles/<uuid:pk>/members/<uuid:mid>/remove/', views.circle_member_remove),
    path('circles/<uuid:pk>/members/<uuid:mid>/promote/', views.member_promote),
    path('circles/<uuid:pk>/members/<uuid:mid>/demote/', views.member_demote),
    path('circles/<uuid:pk>/invites/', views.circle_invites),
    path('circles/<uuid:pk>/invites/<uuid:iid>/deactivate/', views.invite_deactivate),
    path('invites/accept/<str:token>/', views.invite_accept),
    path('invites/info/<str:token>/', views.invite_info),
]
