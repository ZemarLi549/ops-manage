from drf_yasg.inspectors import SwaggerAutoSchema


from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from ops_manage.settings import BASE_URL

class CustomSwaggerAutoSchema(SwaggerAutoSchema):
    def get_tags(self, operation_keys):
        if len(operation_keys) > 2:
            return [operation_keys[0] + '_' + operation_keys[1]]
        return super().get_tags(operation_keys)

    def get_operation_id(self, operation_keys):
        action = ''
        dump_keys = [k for k in operation_keys]
        if hasattr(self.view, 'action'):
            action = self.view.action
            if action == "bulk_destroy":
                action = "bulk_delete"
        if dump_keys[-2] == "children":
            if self.path.find('id') < 0:
                dump_keys.insert(-2, "root")
        if dump_keys[0] == "perms" and dump_keys[1] == "users":
            if self.path.find('{id}') < 0:
                dump_keys.insert(2, "my")
        if action.replace('bulk_', '') == dump_keys[-1]:
            dump_keys[-1] = action
        return super().get_operation_id(tuple(dump_keys))

    def get_operation(self, operation_keys):
        operation = super().get_operation(operation_keys)
        operation.summary = operation.operation_id
        return operation

    def get_filter_parameters(self):
        if not self.should_filter():
            return []

        fields = []
        if hasattr(self.view, 'get_filter_backends'):
            backends = self.view.get_filter_backends()
        elif hasattr(self.view, 'filter_backends'):
            backends = self.view.filter_backends
        else:
            backends = []
        for filter_backend in backends:
            fields += self.probe_inspectors(self.filter_inspectors, 'get_filter_parameters', filter_backend()) or []
        return fields


api_info = openapi.Info(
    title="om API Docs",
    default_version='v1',
    description="om Restful api docs"
)


def get_swagger_view(version='v1'):
    from apps.apis import api_urls
    from django.urls import path, include
    api_patterns = [
        path(BASE_URL, include(api_urls))
    ]
    patterns = api_patterns
    schema_view = get_schema_view(
        api_info,
        patterns=patterns,
        # permission_classes=(permissions.IsAuthenticated,),
    )
    return schema_view

