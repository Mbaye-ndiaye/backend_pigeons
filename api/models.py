from django.db import models
from safedelete.managers import SafeDeleteManager
from safedelete.models import SafeDeleteModel
from safedelete import DELETED_INVISIBLE
from django.contrib.auth.models import AbstractUser, BaseUserManager

SEX_CHOICES = [
    ("M", "Mâle"), ("F", "Femelle")
]
PIGEON_STATUS = [
    ("actif", "Actif"),
    ("vendu", "Vendu"),
    ("mort", "Mort"),
    ("perdu", "Perdu"),
]
SORTIE_TYPES = [
    ("vente", "Vente"),
    ("deces", "Décès"),
    ("perte", "Perte"),
]
ADMIN = "admin"
SUPERADMIN = "superadmin"
DELETED = "deleted"
USER_TYPES = (
    (ADMIN, ADMIN),
    (SUPERADMIN, SUPERADMIN),
    (DELETED, DELETED),
)

class MyModelManager(SafeDeleteManager):
    _safedelete_visibility = DELETED_INVISIBLE


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('user_type', SUPERADMIN)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class Pigeon(models.Model):
    bague = models.CharField(max_length=50, unique=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    race = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    parent_male = models.ForeignKey(
        "self", null=True, blank=True, related_name="children_as_father",
        on_delete=models.SET_NULL, limit_choices_to={"sex": "M"},
    )
    parent_female = models.ForeignKey(
        "self", null=True, blank=True, related_name="children_as_mother",
        on_delete=models.SET_NULL, limit_choices_to={"sex": "F"},
    )
    status = models.CharField(max_length=10, choices=PIGEON_STATUS, default="actif")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bague} ({self.race})"


class Couple(models.Model):
    male = models.ForeignKey(
        Pigeon, related_name="couples_as_male",
        on_delete=models.CASCADE, limit_choices_to={"sex": "M"},
    )
    female = models.ForeignKey(
        Pigeon, related_name="couples_as_female",
        on_delete=models.CASCADE, limit_choices_to={"sex": "F"},
    )
    formed_at = models.DateField()
    active = models.BooleanField(default=True)
    dissolved_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Couple {self.male.bague} x {self.female.bague}"


class Reproduction(models.Model):
    couple = models.ForeignKey(Couple, related_name="reproductions", on_delete=models.CASCADE)
    pond_date = models.DateField()
    hatch_date = models.DateField(null=True, blank=True)
    count = models.PositiveIntegerField(default=0)
    babies = models.ManyToManyField(Pigeon, blank=True, related_name="from_reproduction")
    notes = models.TextField(blank=True, default="")

    def __str__(self):
        return f"Repro {self.couple_id} - {self.pond_date}"


class Sortie(models.Model):
    pigeon = models.ForeignKey(Pigeon, related_name="sorties", on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=SORTIE_TYPES)
    date = models.DateField()
    buyer = models.CharField(max_length=200, blank=True, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reason = models.TextField(blank=True, default="")

    def __str__(self):
        return f"{self.type} - {self.pigeon.bague}"


class Cage(models.Model):
    code = models.CharField(max_length=20, unique=True)
    pigeon = models.OneToOneField(
        Pigeon, null=True, blank=True, related_name="cage", on_delete=models.SET_NULL,
    )
    couple = models.OneToOneField(
        Couple, null=True, blank=True, related_name="cage", on_delete=models.SET_NULL,
    )

    def __str__(self):
        return self.code


class CageEvent(models.Model):
    """Historique d’une cage : affectations, retraits, nettoyage, contrôle sanitaire, etc."""

    class Kind(models.TextChoices):
        PIGEON_ASSIGNED = "pigeon_assigned", "Pigeon affecté"
        PIGEON_REMOVED = "pigeon_removed", "Pigeon retiré de la cage"
        COUPLE_ASSIGNED = "couple_assigned", "Couple affecté"
        COUPLE_REMOVED = "couple_removed", "Couple retiré de la cage"
        CAGE_CLEANED = "cage_cleaned", "Cage nettoyée"
        HEALTH_CHECK = "health_check", "Contrôle sanitaire"

    cage = models.ForeignKey(Cage, on_delete=models.CASCADE, related_name="events")
    kind = models.CharField(max_length=32, choices=Kind.choices)
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.cage.code} — {self.get_kind_display()} @ {self.created_at}"
