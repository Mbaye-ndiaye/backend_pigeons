from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Pigeon, Couple, Reproduction, Sortie, Cage
from .serializers import (
    PigeonSerializer, CoupleSerializer, 
    ReproductionSerializer, SortieSerializer, CageSerializer
)

class PigeonViewSet(viewsets.ModelViewSet):
    queryset = Pigeon.objects.all()
    serializer_class = PigeonSerializer
    permission_classes = [IsAuthenticated]

class CoupleViewSet(viewsets.ModelViewSet):
    queryset = Couple.objects.all()
    serializer_class = CoupleSerializer
    permission_classes = [IsAuthenticated]

class ReproductionViewSet(viewsets.ModelViewSet):
    queryset = Reproduction.objects.all()
    serializer_class = ReproductionSerializer
    permission_classes = [IsAuthenticated]

class SortieViewSet(viewsets.ModelViewSet):
    queryset = Sortie.objects.all()
    serializer_class = SortieSerializer
    permission_classes = [IsAuthenticated]

class CageViewSet(viewsets.ModelViewSet):
    queryset = Cage.objects.all()
    serializer_class = CageSerializer
    permission_classes = [IsAuthenticated]

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    try:
        user = User.objects.get(username=username)
        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {'username': user.username},
            })
        else:
            return Response(
                {'error': 'Mot de passe incorrect'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
    except User.DoesNotExist:
        return Response(
            {'error': 'Utilisateur non trouvé'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stats_view(request):
    pigeons = Pigeon.objects.count()
    couples = Couple.objects.filter(active=True).count()
    reproductions = Reproduction.objects.count()
    sorties = Sortie.objects.count()
    cages = Cage.objects.count()
    
    return Response({
        'pigeons': pigeons,
        'couples': couples,
        'reproductions': reproductions,
        'sorties': sorties,
        'cages': cages,
    })
