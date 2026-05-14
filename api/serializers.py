from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Pigeon, Couple, Reproduction, Sortie, Cage, CageEvent


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class PigeonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pigeon
        fields = "__all__"


class CoupleSerializer(serializers.ModelSerializer):
    male_bague = serializers.CharField(source="male.bague", read_only=True)
    female_bague = serializers.CharField(source="female.bague", read_only=True)

    class Meta:
        model = Couple
        fields = [
            "id", "male", "female", "male_bague", "female_bague",
            "formed_at", "active", "dissolved_at",
        ]


class ReproductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reproduction
        fields = "__all__"


class SortieSerializer(serializers.ModelSerializer):
    pigeon_bague = serializers.CharField(source="pigeon.bague", read_only=True)
    buyer = serializers.CharField(allow_blank=True, required=False, default="", allow_null=True)
    reason = serializers.CharField(allow_blank=True, required=False, default="", allow_null=True)

    class Meta:
        model = Sortie
        fields = [
            "id", "pigeon", "pigeon_bague", "type", "date",
            "buyer", "price", "reason",
        ]

    def validate(self, attrs):
        """Le modèle n’enregistre pas NULL sur buyer/reason (CharField / TextField)."""
        if attrs.get("buyer") is None:
            attrs["buyer"] = ""
        if attrs.get("reason") is None:
            attrs["reason"] = ""
        return attrs


class CageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cage
        fields = "__all__"


class CageEventSerializer(serializers.ModelSerializer):
    """Événement d’historique : libellé français via `text` (get_kind_display)."""

    text = serializers.CharField(source="get_kind_display", read_only=True)

    class Meta:
        model = CageEvent
        fields = ["id", "kind", "text", "meta", "created_at"]
        read_only_fields = ["id", "created_at"]
