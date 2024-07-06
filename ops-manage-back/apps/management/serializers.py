from rest_framework import serializers
from .models import *


class OpsTokener(serializers.ModelSerializer):
    class Meta:
        model = OpsToken
        fields = "__all__"


class Departmenter(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class Resourceer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = "__all__"

class Roleer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class Userer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"