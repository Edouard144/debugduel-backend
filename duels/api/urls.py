from django.urls import path
from .views import CreateDuelView, JoinDuelView, DuelDetailView

urlpatterns = [
    path('create/', CreateDuelView.as_view(), name='create_duel'),
    path('<str:code>/join/', JoinDuelView.as_view(), name='join_duel'),
    path('<str:code>/', DuelDetailView.as_view(), name='duel_detail'),
]