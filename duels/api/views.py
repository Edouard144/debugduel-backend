from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from duels.models import DuelRoom
from .serializers import DuelRoomSerializer
import random
import string

def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class CreateDuelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        language = request.data.get('language', 'python')
        difficulty = request.data.get('difficulty', 'easy')
        code = generate_room_code()
        while DuelRoom.objects.filter(code=code).exists():
            code = generate_room_code()
        room = DuelRoom.objects.create(
            creator=request.user,
            code=code,
            language=language,
            difficulty=difficulty
        )
        return Response(DuelRoomSerializer(room).data, status=status.HTTP_201_CREATED)

class JoinDuelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, code):
        try:
            room = DuelRoom.objects.get(code=code, status='waiting')
        except DuelRoom.DoesNotExist:
            return Response({'error': 'Room not found or already started'}, status=status.HTTP_404_NOT_FOUND)
        if room.creator == request.user:
            return Response({'error': 'You cannot join your own room'}, status=status.HTTP_400_BAD_REQUEST)
        room.opponent = request.user
        room.status = 'active'
        room.save()
        return Response(DuelRoomSerializer(room).data)

class DuelDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, code):
        try:
            room = DuelRoom.objects.get(code=code)
        except DuelRoom.DoesNotExist:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(DuelRoomSerializer(room).data)