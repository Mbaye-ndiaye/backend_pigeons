from django.contrib import admin
from .models import Pigeon, Couple, Reproduction, Sortie, Cage, CageEvent

admin.site.register(Pigeon)
admin.site.register(Couple)
admin.site.register(Reproduction)
admin.site.register(Sortie)
admin.site.register(Cage)
admin.site.register(CageEvent)
