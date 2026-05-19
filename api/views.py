from datetime import date
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Count, Sum, Q

from .models import Pigeon, Couple, Reproduction, Sortie, Cage, User
from .serializers import (
    PigeonSerializer, CoupleSerializer, ReproductionSerializer,
    SortieSerializer, CageSerializer, UserSerializer, CustomTokenObtainPairSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def me(request):
    if not request.user.is_authenticated:
        return Response({"detail": "Not authenticated"}, status=401)
    return Response(UserSerializer(request.user).data)


class PigeonViewSet(viewsets.ModelViewSet):
    serializer_class = PigeonSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = Pigeon.objects.filter(user=self.request.user).order_by("-created_at")
        sex = self.request.query_params.get("sex")
        st = self.request.query_params.get("status")
        race = self.request.query_params.get("race")
        search = self.request.query_params.get("search")
        if sex:
            qs = qs.filter(sex=sex)
        if st:
            qs = qs.filter(status=st)
        if race:
            qs = qs.filter(race__icontains=race)
        if search:
            qs = qs.filter(Q(bague__icontains=search) | Q(race__icontains=search))
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["get"])
    def descendants(self, request, pk=None):
        pigeon = self.get_object()
        children = Pigeon.objects.filter(
            Q(parent_male=pigeon) | Q(parent_female=pigeon)
        )
        return Response(PigeonSerializer(children, many=True).data)


class CoupleViewSet(viewsets.ModelViewSet):
    serializer_class = CoupleSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = Couple.objects.filter(user=self.request.user).order_by("-formed_at")
        active = self.request.query_params.get("active")
        if active is not None:
            qs = qs.filter(active=active.lower() in ("1", "true", "yes"))
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def dissolve(self, request, pk=None):
        couple = self.get_object()
        couple.active = False
        couple.dissolved_at = date.today()
        couple.save()
        # free cage
        Cage.objects.filter(couple=couple).update(couple=None)
        return Response(CoupleSerializer(couple).data)


class ReproductionViewSet(viewsets.ModelViewSet):
    serializer_class = ReproductionSerializer

    def get_queryset(self):
        qs = Reproduction.objects.filter(user=self.request.user).order_by("-pond_date")
        couple = self.request.query_params.get("couple")
        if couple:
            qs = qs.filter(couple_id=couple)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SortieViewSet(viewsets.ModelViewSet):
    serializer_class = SortieSerializer

    def get_queryset(self):
        return Sortie.objects.filter(user=self.request.user).order_by("-date")

    def perform_create(self, serializer):
        sortie = serializer.save(user=self.request.user)
        mapping = {"vente": "vendu", "deces": "mort", "perte": "perdu"}
        Pigeon.objects.filter(id=sortie.pigeon_id).update(
            status=mapping.get(sortie.type, "actif")
        )
        Cage.objects.filter(pigeon=sortie.pigeon).update(pigeon=None)


class CageViewSet(viewsets.ModelViewSet):
    serializer_class = CageSerializer

    def get_queryset(self):
        return Cage.objects.filter(user=self.request.user).order_by("code")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        cage = self.get_object()
        kind = request.data.get("kind")  # "pigeon" or "couple"
        ref_id = request.data.get("ref_id")
        if kind not in ("pigeon", "couple") or not ref_id:
            return Response({"detail": "kind & ref_id required"}, status=400)
        # free other cages holding this ref
        if kind == "pigeon":
            Cage.objects.filter(pigeon_id=ref_id).update(pigeon=None)
            cage.pigeon_id = ref_id
            cage.couple = None
        else:
            Cage.objects.filter(couple_id=ref_id).update(couple=None)
            cage.couple_id = ref_id
            cage.pigeon = None
        cage.save()
        return Response(CageSerializer(cage).data)

    @action(detail=True, methods=["post"])
    def free(self, request, pk=None):
        cage = self.get_object()
        cage.pigeon = None
        cage.couple = None
        cage.save()
        return Response(CageSerializer(cage).data)


@api_view(["GET"])
def dashboard_stats(request):
    user = request.user
    pigeons = Pigeon.objects.filter(user=user)
    return Response({
        "total_pigeons": pigeons.count(),
        "by_status": list(pigeons.values("status").annotate(count=Count("id"))),
        "by_sex": list(pigeons.values("sex").annotate(count=Count("id"))),
        "by_race": list(pigeons.values("race").annotate(count=Count("id"))),
        "active_couples": Couple.objects.filter(user=user, active=True).count(),
        "total_reproductions": Reproduction.objects.filter(user=user).count(),
        "total_babies": Reproduction.objects.filter(user=user).aggregate(total=Sum("count"))["total"] or 0,
        "cages_total": Cage.objects.filter(user=user).count(),
        "cages_occupied": Cage.objects.filter(user=user).filter(
            Q(pigeon__isnull=False) | Q(couple__isnull=False)
        ).count(),
        "sales_total": float(
            Sortie.objects.filter(user=user, type="vente").aggregate(s=Sum("price"))["s"] or 0
        ),
    })
