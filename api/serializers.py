from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Pigeon, Couple, Reproduction, Sortie, Cage, CageEvent, User


# --- JWT personnalisé : utilise email au lieu de username ---
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD  # 'email'


# --- Serializer inscription superadmin ---
class CreateSuperAdminSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    username = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value

    def create(self, validated_data):
        return User.objects.create_superuser(
            email=validated_data['email'],
            password=validated_data['password'],
            username=validated_data.get('username', ''),
            user_type='superadmin',
            is_staff=True,
            is_active=True
        )


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    username = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data.get('email'),
            password=validated_data.get('password'),
            username=validated_data.get('username', ''),
        )
        return user


class PigeonSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Pigeon
        # Exclude 'user' — it's set automatically in the view via perform_create
        exclude = ["user"]


class CoupleSerializer(serializers.ModelSerializer):
    # Write-only IDs for creating/updating
    male_id = serializers.IntegerField(write_only=True, required=False)
    female_id = serializers.IntegerField(write_only=True, required=False)
    # Read-only nested objects
    male = PigeonSerializer(read_only=True)
    female = PigeonSerializer(read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Couple
        fields = [
            "id", "male", "female", "male_id", "female_id",
            "formed_at", "active", "dissolved_at", "image",
        ]

    def create(self, validated_data):
        male_id = validated_data.pop('male_id', None)
        female_id = validated_data.pop('female_id', None)
        if male_id:
            validated_data['male_id'] = male_id
        if female_id:
            validated_data['female_id'] = female_id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        male_id = validated_data.pop('male_id', None)
        female_id = validated_data.pop('female_id', None)
        if male_id:
            validated_data['male_id'] = male_id
        if female_id:
            validated_data['female_id'] = female_id
        return super().update(instance, validated_data)


class ReproductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reproduction
        exclude = ["user"]

    def validate(self, attrs):
        """La date d'éclosion ne peut pas être avant la date de ponte."""
        pond_date = attrs.get('pond_date')
        hatch_date = attrs.get('hatch_date')
        if hatch_date and pond_date and hatch_date < pond_date:
            raise serializers.ValidationError({
                'hatch_date': "La date d'éclosion ne peut pas être avant la date de ponte."
            })
        return attrs


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

    def validate_price(self, value):
        """Le prix ne peut pas être négatif."""
        if value is not None and value < 0:
            raise serializers.ValidationError("Le prix ne peut pas être négatif.")
        return value

    def validate(self, attrs):
        if attrs.get("buyer") is None:
            attrs["buyer"] = ""
        if attrs.get("reason") is None:
            attrs["reason"] = ""
        return attrs


class CageSerializer(serializers.ModelSerializer):
    pigeon_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    couple_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    pigeon = PigeonSerializer(read_only=True)
    couple = CoupleSerializer(read_only=True)

    class Meta:
        model = Cage
        fields = ["id", "code", "pigeon", "couple", "pigeon_id", "couple_id"]

    def validate(self, attrs):
        pigeon_id = attrs.get('pigeon_id')
        couple_id = attrs.get('couple_id')
        if pigeon_id and couple_id:
            raise serializers.ValidationError(
                "Une cage ne peut pas contenir à la fois un pigeon et un couple."
            )
        return attrs

    def create(self, validated_data):
        pigeon_id = validated_data.pop('pigeon_id', None)
        couple_id = validated_data.pop('couple_id', None)
        cage = Cage.objects.create(**validated_data)
        if pigeon_id:
            cage.pigeon_id = pigeon_id
        if couple_id:
            cage.couple_id = couple_id
        cage.save()
        return cage

    def update(self, instance, validated_data):
        pigeon_id = validated_data.pop('pigeon_id', None)
        couple_id = validated_data.pop('couple_id', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if 'pigeon_id' in self.initial_data:
            instance.pigeon_id = pigeon_id
        if 'couple_id' in self.initial_data:
            instance.couple_id = couple_id
        instance.save()
        return instance


class CageEventSerializer(serializers.ModelSerializer):
    text = serializers.CharField(source="get_kind_display", read_only=True)

    class Meta:
        model = CageEvent
        fields = ["id", "kind", "text", "meta", "created_at"]
        read_only_fields = ["id", "created_at"]
