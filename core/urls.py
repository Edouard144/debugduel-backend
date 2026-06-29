from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def health_check(request):
    return Response({'status': 'ok', 'project': 'DebugDuel Backend', 'version': '1.0.0'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check),
    path('api/auth/', include('users.api.urls')),
    path('api/duels/', include('duels.api.urls')),
]
