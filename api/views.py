from datetime import date
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Pigeon, Couple, Reproduction, Sortie, Cage, CageEvent
from .serializers import (
    PigeonSerializer, CoupleSerializer, ReproductionSerializer,
    SortieSerializer, CageSerializer, CageEventSerializer, UserSerializer,
)
from .cage_journal import log_cage_transitions


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
        # free cage + journal
        for c in Cage.objects.filter(couple=couple):
            old_p, old_c = c.pigeon_id, c.couple_id
            c.couple = None
            c.save()
            c.refresh_from_db()
            log_cage_transitions(c, old_p, old_c)
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
        for c in Cage.objects.filter(pigeon=sortie.pigeon):
            old_p, old_c = c.pigeon_id, c.couple_id
            c.pigeon = None
            c.save()
            c.refresh_from_db()
            log_cage_transitions(c, old_p, old_c)


class CageViewSet(viewsets.ModelViewSet):
    queryset = Cage.objects.all().order_by("code")
    serializer_class = CageSerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_p, old_c = instance.pigeon_id, instance.couple_id
        response = super().partial_update(request, *args, **kwargs)
        instance.refresh_from_db()
        log_cage_transitions(instance, old_p, old_c)
        return response

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_p, old_c = instance.pigeon_id, instance.couple_id
        response = super().update(request, *args, **kwargs)
        instance.refresh_from_db()
        log_cage_transitions(instance, old_p, old_c)
        return response

    @action(detail=True, methods=["get", "post"], url_path="history")
    def history(self, request, pk=None):
        cage = self.get_object()
        if request.method == "GET":
            events = CageEvent.objects.filter(cage=cage)[:200]
            return Response(CageEventSerializer(events, many=True).data)
        allowed = {CageEvent.Kind.CAGE_CLEANED.value, CageEvent.Kind.HEALTH_CHECK.value}
        if kind not in allowed:
            return Response(
                {"detail": f"kind doit être l'un de : {', '.join(sorted(allowed))}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ev = CageEvent.objects.create(cage=cage, kind=kind)
        return Response(CageEventSerializer(ev).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        cage = self.get_object()
        kind = request.data.get("kind")  # "pigeon" or "couple"
        ref_id = request.data.get("ref_id")
        if kind not in ("pigeon", "couple") or not ref_id:
            return Response({"detail": "kind & ref_id required"}, status=400)
        try:
            ref_id = int(ref_id)
        except (TypeError, ValueError):
            return Response({"detail": "ref_id invalide"}, status=400)

        if kind == "pigeon":
            for oc in Cage.objects.filter(pigeon_id=ref_id).exclude(pk=cage.pk):
                op, ocl = oc.pigeon_id, oc.couple_id
                oc.pigeon = None
                oc.save()
                oc.refresh_from_db()
                log_cage_transitions(oc, op, ocl)
            old_p, old_c = cage.pigeon_id, cage.couple_id
            cage.pigeon_id = ref_id
            cage.couple = None
            cage.save()
            cage.refresh_from_db()
            log_cage_transitions(cage, old_p, old_c)
        else:
            for oc in Cage.objects.filter(couple_id=ref_id).exclude(pk=cage.pk):
                op, ocl = oc.pigeon_id, oc.couple_id
                oc.couple = None
                oc.save()
                oc.refresh_from_db()
                log_cage_transitions(oc, op, ocl)
            old_p, old_c = cage.pigeon_id, cage.couple_id
            cage.couple_id = ref_id
            cage.pigeon = None
            cage.save()
            cage.refresh_from_db()
            log_cage_transitions(cage, old_p, old_c)
        return Response(CageSerializer(cage).data)

    @action(detail=True, methods=["post"])
    def free(self, request, pk=None):
        cage = self.get_object()
        old_p, old_c = cage.pigeon_id, cage.couple_id
        cage.pigeon = None
        cage.couple = None
        cage.save()
        cage.refresh_from_db()
        log_cage_transitions(cage, old_p, old_c)
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
