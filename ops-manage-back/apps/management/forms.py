from rest_framework import serializers

class BaseForm(serializers.Serializer):
    # simple serializer for base
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=64)


class ResourcePostForm(serializers.Serializer):
    # simple serializer for base
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=64)
    res_type = serializers.ChoiceField(choices=[('ui', 'ui'), ('api', 'api')])


class ResourceGetForm(serializers.Serializer):
    # simple serializer for base
    id = serializers.IntegerField(required=False)
    parent_id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=64,required=False)
    description = serializers.CharField(max_length=64,required=False)
    code = serializers.CharField(max_length=64,required=False)
    res_type = serializers.ChoiceField(choices=[('ui', 'ui'), ('api', 'api')],required=False)


class UserGetForm(serializers.Serializer):
    # simple serializer for userget
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=64,required=False)


class RoleGetForm(serializers.Serializer):
    # simple serializer for userget
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=64,required=False)
    description = serializers.CharField(max_length=64,required=False)

class PutBaseForm(serializers.Serializer):
    # simple serializer for base
    id = serializers.IntegerField(required=True)


class ResourceRolePutForm(PutBaseForm):
    # simple serializer for base
    resource_id = serializers.IntegerField(required=False)
    user_id = serializers.IntegerField(required=False)


class DeleteBaseForm(serializers.Serializer):
    # simple serializer for base
    id = serializers.IntegerField(required=True)


class LoginPostForm(serializers.Serializer):
    # simple serializer for base
    username = serializers.CharField(max_length=64)
    password = serializers.CharField(max_length=64)


class LogoutForm(serializers.Serializer):
    # simple serializer for base
    username = serializers.CharField(max_length=64,required=False)

class TokenForm(serializers.Serializer):
    # simple serializer for base
    user_token = serializers.CharField(max_length=600)


class UserRolePostForm(serializers.Serializer):
    # simple serializer for base
    user_id = serializers.IntegerField(required=True)
    role_id = serializers.IntegerField(required=True)
    name = serializers.CharField(max_length=64, required=False)


class ResourceRolePostForm(serializers.Serializer):
    # simple serializer for base
    resource_id = serializers.IntegerField(required=True)
    role_id = serializers.IntegerField(required=True)
    name = serializers.CharField(max_length=64, required=False)


class UserRoleGetForm(serializers.Serializer):
    # simple serializer for base
    user_id = serializers.IntegerField(required=False)
    role_id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=64, required=False)


class ResourceRoleGetForm(serializers.Serializer):
    # simple serializer for base
    resource_id = serializers.IntegerField(required=False)
    role_id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=64, required=False)


class UserRolePutForm(serializers.Serializer):
    # simple serializer for base
    user_id = serializers.IntegerField(required=False)
    role_id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=64, required=False)



