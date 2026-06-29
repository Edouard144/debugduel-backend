from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from duels.models import DuelRoom, Submission
from .serializers import DuelRoomSerializer, SubmissionSerializer
from duels.judge import judge_submissions
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

class SubmitCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, code):
        try:
            room = DuelRoom.objects.get(code=code, status='active')
        except DuelRoom.DoesNotExist:
            return Response({'error': 'Active room not found'}, status=status.HTTP_404_NOT_FOUND)
        if request.user != room.creator and request.user != room.opponent:
            return Response({'error': 'You are not a player in this room'}, status=status.HTTP_403_FORBIDDEN)
        existing = Submission.objects.filter(room=room, player=request.user).first()
        if existing:
            return Response({'error': 'You already submitted'}, status=status.HTTP_400_BAD_REQUEST)
        submission = Submission.objects.create(
            room=room,
            player=request.user,
            code=request.data.get('code', '')
        )
        submissions = Submission.objects.filter(room=room)
        if submissions.count() == 2:
            room.status = 'judging'
            room.save()
            subs = list(submissions)
            creator_sub = next(s for s in subs if s.player == room.creator)
            opponent_sub = next(s for s in subs if s.player == room.opponent)
            try:
                result = judge_submissions(
                    buggy_code=room.buggy_code,
                    submission1=creator_sub.code,
                    submission2=opponent_sub.code,
                    language=room.language
                )
                winner = result['winner']
                p1 = result['player1']
                p2 = result['player2']

                creator_sub.correctness = p1['correctness']
                creator_sub.cleanliness = p1['cleanliness']
                creator_sub.efficiency = p1['efficiency']
                creator_sub.security = p1['security']
                creator_sub.score = p1['score']
                creator_sub.ai_feedback = p1['feedback']
                creator_sub.is_winner = winner == 'player1'
                creator_sub.save()

                opponent_sub.correctness = p2['correctness']
                opponent_sub.cleanliness = p2['cleanliness']
                opponent_sub.efficiency = p2['efficiency']
                opponent_sub.security = p2['security']
                opponent_sub.score = p2['score']
                opponent_sub.ai_feedback = p2['feedback']
                opponent_sub.is_winner = winner == 'player2'
                opponent_sub.save()

                room.creator.total_duels += 1
                room.opponent.total_duels += 1
                if winner == 'player1':
                    room.creator.wins += 1
                    room.opponent.losses += 1
                else:
                    room.opponent.wins += 1
                    room.creator.losses += 1
                room.creator.save()
                room.opponent.save()

                room.status = 'finished'
                room.save()
            except Exception as e:
                room.status = 'finished'
                room.save()
                return Response({'error': f'Judging failed: {str(e)}'}, status=500)
        return Response(SubmissionSerializer(submission).data, status=status.HTTP_201_CREATED)

class RoomSubmissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, code):
        try:
            room = DuelRoom.objects.get(code=code)
        except DuelRoom.DoesNotExist:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
        submissions = Submission.objects.filter(room=room)
        return Response(SubmissionSerializer(submissions, many=True).data)