from datetime import date
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
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
    queryset = Pigeon.objects.all().order_by("-created_at")
    serializer_class = PigeonSerializer

    def get_queryset(self):
        qs = super().get_queryset()
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

    @action(detail=True, methods=["get"])
    def descendants(self, request, pk=None):
        pigeon = self.get_object()
        children = Pigeon.objects.filter(
            Q(parent_male=pigeon) | Q(parent_female=pigeon)
        )
        return Response(PigeonSerializer(children, many=True).data)


class CoupleViewSet(viewsets.ModelViewSet):
    queryset = Couple.objects.all().order_by("-formed_at")
    serializer_class = CoupleSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        active = self.request.query_params.get("active")
        if active is not None:
            qs = qs.filter(active=active.lower() in ("1", "true", "yes"))
        return qs

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
    queryset = Reproduction.objects.all().order_by("-pond_date")
    serializer_class = ReproductionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        couple = self.request.query_params.get("couple")
        if couple:
            qs = qs.filter(couple_id=couple)
        return qs


class SortieViewSet(viewsets.ModelViewSet):
    queryset = Sortie.objects.all().order_by("-date")
    serializer_class = SortieSerializer

    def perform_create(self, serializer):
        sortie = serializer.save()
        mapping = {"vente": "vendu", "deces": "mort", "perte": "perdu"}
        Pigeon.objects.filter(id=sortie.pigeon_id).update(
            status=mapping.get(sortie.type, "actif")
        )
        Cage.objects.filter(pigeon=sortie.pigeon).update(pigeon=None)


class CageViewSet(viewsets.ModelViewSet):
    queryset = Cage.objects.all().order_by("code")
    serializer_class = CageSerializer

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
    pigeons = Pigeon.objects.all()
    return Response({
        "total_pigeons": pigeons.count(),
        "by_status": list(pigeons.values("status").annotate(count=Count("id"))),
        "by_sex": list(pigeons.values("sex").annotate(count=Count("id"))),
        "by_race": list(pigeons.values("race").annotate(count=Count("id"))),
        "active_couples": Couple.objects.filter(active=True).count(),
        "total_reproductions": Reproduction.objects.count(),
        "total_babies": Reproduction.objects.aggregate(total=Sum("count"))["total"] or 0,
        "cages_total": Cage.objects.count(),
        "cages_occupied": Cage.objects.filter(
            Q(pigeon__isnull=False) | Q(couple__isnull=False)
        ).count(),
        "sales_total": float(
            Sortie.objects.filter(type="vente").aggregate(s=Sum("price"))["s"] or 0
        ),
    })
