from rest_framework import serializers
from .models import *


class DataSourceer(serializers.ModelSerializer):
    class Meta:
        model = DataSource
        fields = "__all__"


class AppConfiger(serializers.ModelSerializer):
    class Meta:
        model = AppConfig
        fields = "__all__"


class GateConfiger(serializers.ModelSerializer):
    class Meta:
        model = GateConfig
        fields = "__all__"


class ComponentIndexer(serializers.ModelSerializer):
    class Meta:
        model = ComponentIndex
        fields = "__all__"

class GatePasser(serializers.ModelSerializer):
    class Meta:
        model = GatePass
        fields = "__all__"

class AppPasser(serializers.ModelSerializer):
    class Meta:
        model = AppPass
        fields = "__all__"