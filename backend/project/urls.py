from django.urls import path, include
from django.http import JsonResponse


def api_root(request):
    return JsonResponse({'message': 'Hello World'})


urlpatterns = [
    path('api/', api_root),
    path('api/private/', include('accounts.urls')),
    path('api/private/', include('circles.urls')),
    path('api/private/', include('events.urls')),
]
