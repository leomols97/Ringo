from django.urls import path
from . import views

urlpatterns = [
    path('events/active/', views.active_circle_events),
    path('events/public/', views.public_events),
    path('circles/<uuid:circle_id>/events/', views.circle_events),
    path('events/<uuid:eid>/', views.event_detail),
    path('events/<uuid:eid>/signup/', views.event_signup),
    path('events/<uuid:eid>/signups/', views.event_signups),
    path('signups/<uuid:sid>/approve/', views.signup_approve),
    path('signups/<uuid:sid>/reject/', views.signup_reject),
]
