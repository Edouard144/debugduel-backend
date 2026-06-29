from rest_framework import serializers
from duels.models import DuelRoom
from users.api.serializers import UserSerializer

class DuelRoomSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    opponent = UserSerializer(read_only=True)

    class Meta:
        model = DuelRoom
        fields = ['id', 'code', 'creator', 'opponent', 'status', 'language', 'difficulty', 'buggy_code', 'started_at', 'finished_at', 'created_at']