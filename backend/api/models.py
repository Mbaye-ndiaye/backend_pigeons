from django.db import models

class Pigeon(models.Model):
    bague = models.CharField(max_length=50)
    sex = models.CharField(max_length=1, choices=[('M', 'Mâle'), ('F', 'Femelle')])
    race = models.CharField(max_length=100)
    birth_date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('actif', 'Actif'),
        ('vendu', 'Vendu'),
        ('decede', 'Décédé'),
        ('perdu', 'Perdu')
    ])
    parent_male = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='male_children')
    parent_female = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='female_children')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pigeons'

    def __str__(self):
        return f"{self.bague} - {self.race}"

class Couple(models.Model):
    male = models.ForeignKey(Pigeon, on_delete=models.CASCADE, related_name='male_couples')
    female = models.ForeignKey(Pigeon, on_delete=models.CASCADE, related_name='female_couples')
    formed_at = models.DateField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'couples'

    def __str__(self):
        return f"Couple {self.id}"

class Reproduction(models.Model):
    couple = models.ForeignKey(Couple, on_delete=models.CASCADE)
    pond_date = models.DateField()
    hatch_date = models.DateField(null=True, blank=True)
    count = models.IntegerField(default=2)
    baby_ids = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reproductions'

    def __str__(self):
        return f"Reproduction {self.id}"

class Sortie(models.Model):
    pigeon = models.ForeignKey(Pigeon, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=[
        ('vente', 'Vente'),
        ('deces', 'Décès'),
        ('perte', 'Perte')
    ])
    date = models.DateField()
    buyer = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reason = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sorties'

    def __str__(self):
        return f"Sortie {self.id}"

class Cage(models.Model):
    row = models.CharField(max_length=1)
    col = models.IntegerField()
    pigeon = models.ForeignKey(Pigeon, on_delete=models.CASCADE, null=True, blank=True)
    couple = models.ForeignKey(Couple, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cages'

    def __str__(self):
        return f"Cage {self.row}{self.col}"
