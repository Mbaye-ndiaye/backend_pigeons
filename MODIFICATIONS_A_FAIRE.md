# 📋 Modifications à apporter au projet Volière

## ✅ Corrections déjà effectuées

1. **Validation des dates de reproduction** - Backend
   - La date d'éclosion ne peut plus être avant la date de ponte
   
2. **Validation du prix** - Backend
   - Le prix ne peut plus être négatif dans les sorties

3. **Ajout du champ image dans les serializers** - Backend
   - PigeonSerializer et CoupleSerializer acceptent maintenant les images

## 🔧 Modifications à faire manuellement

### 1. Ajouter les champs aux modèles (models.py)

```python
class Pigeon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pigeons")
    bague = models.CharField(max_length=50)
    nom = models.CharField(max_length=100, blank=True, default="")
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    race = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='pigeons/', null=True, blank=True)
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

    class Meta:
        unique_together = ['user', 'bague']  # Bague unique par utilisateur

    def __str__(self):
        return f"{self.nom or self.bague} ({self.race})"


class Couple(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="couples")
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
    image = models.ImageField(upload_to='couples/', null=True, blank=True)

    def __str__(self):
        return f"Couple {self.male.bague} x {self.female.bague}"


class Reproduction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reproductions")
    couple = models.ForeignKey(Couple, related_name="reproductions", on_delete=models.CASCADE)
    pond_date = models.DateField()
    hatch_date = models.DateField(null=True, blank=True)
    count = models.PositiveIntegerField(default=0)
    babies = models.ManyToManyField(Pigeon, blank=True, related_name="from_reproduction")
    notes = models.TextField(blank=True, default="")

    def __str__(self):
        return f"Reproduction {self.couple} - {self.pond_date}"


class Sortie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sorties")
    pigeon = models.ForeignKey(Pigeon, related_name="sorties", on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=SORTIE_TYPES)
    date = models.DateField()
    buyer = models.CharField(max_length=200, blank=True, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reason = models.TextField(blank=True, default="")

    def __str__(self):
        return f"{self.type} - {self.pigeon.bague}"


class Cage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cages")
    code = models.CharField(max_length=20)
    pigeon = models.OneToOneField(
        Pigeon, null=True, blank=True, related_name="cage", on_delete=models.SET_NULL,
    )
    couple = models.OneToOneField(
        Couple, null=True, blank=True, related_name="cage", on_delete=models.SET_NULL,
    )

    class Meta:
        unique_together = ['user', 'code']  # Code unique par utilisateur

    def __str__(self):
        return self.code
```

### 2. Configuration des médias (settings.py)

Ajouter à la fin du fichier :

```python
# Configuration des médias (images)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### 3. URLs pour servir les médias (backend/urls.py)

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... vos URLs existantes
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 4. Installer Pillow

```bash
pip install Pillow
pip freeze > requirements.txt
```

### 5. Créer et appliquer les migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Filtrer les données par utilisateur (views.py)

Modifier chaque ViewSet pour filtrer par utilisateur :

```python
class PigeonViewSet(viewsets.ModelViewSet):
    queryset = Pigeon.objects.all().order_by("-created_at")
    serializer_class = PigeonSerializer

    def get_queryset(self):
        # Filtrer par utilisateur connecté
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Associer automatiquement l'utilisateur
        serializer.save(user=self.request.user)


class CoupleViewSet(viewsets.ModelViewSet):
    queryset = Couple.objects.all().order_by("-formed_at")
    serializer_class = CoupleSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReproductionViewSet(viewsets.ModelViewSet):
    queryset = Reproduction.objects.all().order_by("-pond_date")
    serializer_class = ReproductionSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SortieViewSet(viewsets.ModelViewSet):
    queryset = Sortie.objects.all().order_by("-date")
    serializer_class = SortieSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        sortie = serializer.save(user=self.request.user)
        # ... reste du code


class CageViewSet(viewsets.ModelViewSet):
    queryset = Cage.objects.all().order_by("code")
    serializer_class = CageSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
```

### 7. Validation frontend des dates (app.reproductions.jsx)

```javascript
const submit = async (e) => {
  e.preventDefault();
  if (!coupleId) return;

  // Validation des dates
  if (hatchDate && pondDate) {
    const pond = new Date(pondDate);
    const hatch = new Date(hatchDate);
    
    if (hatch < pond) {
      toast.error("La date d'éclosion ne peut pas être avant la date de ponte");
      return;
    }
  }

  try {
    await createReproduction({
      couple: parseInt(coupleId, 10),
      pond_date: pondDate,
      hatch_date: hatchDate || null,
      count,
      baby_ids: [],
    }).unwrap();

    onClose();
    toast.success("Reproduction enregistrée avec succès");
  } catch (error) {
    console.error("Erreur lors de la création de la reproduction:", error);
    toast.error("Erreur lors de l'enregistrement de la reproduction");
  }
};
```

### 8. Validation frontend du prix (app.sorties.jsx)

Ajouter dans le formulaire :

```javascript
<Input
  type="number"
  min="0"
  step="0.01"
  value={price}
  onChange={(e) => setPrice(e.target.value)}
/>
```

## 📝 Ordre d'exécution recommandé

1. ✅ Installer Pillow
2. ✅ Modifier models.py (ajouter user et image)
3. ✅ Modifier settings.py (MEDIA_URL et MEDIA_ROOT)
4. ✅ Modifier backend/urls.py (ajouter static pour media)
5. ✅ Créer et appliquer les migrations
6. ✅ Modifier views.py (filtrer par utilisateur)
7. ✅ Tester le backend
8. ✅ Ajouter validations frontend
9. ✅ Ajouter upload d'images dans le frontend

## ⚠️ Important

- Après avoir ajouté le champ `user`, toutes les données existantes devront être associées à un utilisateur
- Vous pouvez créer une migration de données pour associer toutes les données existantes à un utilisateur par défaut
- Les images seront stockées dans le dossier `media/` à la racine du projet
