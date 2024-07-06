from rest_framework import serializers
from .models import *


class AlarmUserer(serializers.ModelSerializer):
    class Meta:
        model = AlarmUser
        fields = "__all__"


class AlarmConfiger(serializers.ModelSerializer):
    class Meta:
        model = AlarmConfig
        fields = "__all__"


class AlarmRuleer(serializers.ModelSerializer):
    class Meta:
        model = AlarmRule
        fields = "__all__"


class AlarmIdentityer(serializers.ModelSerializer):
    class Meta:
        model = AlarmIdentity
        fields = "__all__"


# class AlarmSolutioner(serializers.ModelSerializer):
#     class Meta:
#         model = AlarmSolution
#         fields = "__all__"
class AlarmZongjieer(serializers.ModelSerializer):
    class Meta:
        model = AlarmZongjie
        fields = "__all__"

class AlarmCommenter(serializers.ModelSerializer):
    class Meta:
        model = AlarmComment
        fields = "__all__"

class AlarmBlacker(serializers.ModelSerializer):
    class Meta:
        model = AlarmBlack
        fields = "__all__"

class CacheReader(serializers.ModelSerializer):
    class Meta:
        model = CacheRead
        fields = "__all__"

