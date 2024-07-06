from rest_framework import serializers
from .models import *


class Clusterer(serializers.ModelSerializer):
    class Meta:
        model = Cluster
        fields = "__all__"
