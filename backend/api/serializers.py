from rest_framework import serializers
from .models import Pigeon, Couple, Reproduction, Sortie, Cage

class PigeonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pigeon
        fields = '__all__'

class CoupleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Couple
        fields = '__all__'

class ReproductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reproduction
        fields = '__all__'

class SortieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sortie
        fields = '__all__'

class CageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cage
        fields = '__all__'
