# -*- coding: utf-8 -*-
import coreapi
import coreschema
from rest_framework.schemas import AutoSchema

page_query_fields = (
    coreapi.Field('page', location='query', schema=coreschema.String(description='page')),
    coreapi.Field('limit', location='query', schema=coreschema.String(description='limit')),
    coreapi.Field('order', location='query', schema=coreschema.String(description='order')),
)

pk_id_field = coreapi.Field('id', location='path', required=True, schema=coreschema.String(description='指定 ID'))


class UserViewSchema(AutoSchema):
    def get_link(self, path, method, base_url):
        link = super().get_link(path, method, base_url)
        # Do something to customize link here...
        # print(path, method, base_url)

        user_view_get = (
            coreapi.Field('name', location='query', schema=coreschema.String(description='name')),
            coreapi.Field('search_type', location='query', schema=coreschema.String(description='search_type')),
            coreapi.Field('search_value_type', location='query', schema=coreschema.String(description='search_value_type')),
            coreapi.Field('search_value', location='query', schema=coreschema.String(description='search_value')),
            coreapi.Field('id', location='query', schema=coreschema.Integer(description='id，用于单个查询')),
            coreapi.Field('page_no', location='query', schema=coreschema.String(description='页号')),
            coreapi.Field('page_size', location='query', schema=coreschema.String(description='每页条数')),
        )

        user_view_post = (
            coreapi.Field('name', location='form', required=True, schema=coreschema.String(description='name')),
            coreapi.Field('description', location='form', required=True, schema=coreschema.String(description='description')),
        )

        user_view_put = (
            coreapi.Field('name', location='body', schema=coreschema.String(description='name')),
            coreapi.Field('description', location='body', schema=coreschema.String(description='description')),
            coreapi.Field('id', location='body', required=True, schema=coreschema.Integer(description='id')),
        )

        user_view_delete = (
            coreapi.Field('id', location='body', required=True, schema=coreschema.Integer(description='id')),
        )

        fields = []
        description = ''
        if link.url == f'/pangu/api/user' and method.lower() == 'get':
            fields = user_view_get + link.fields
            description = '根据条件查询user'
        if link.url == f'/pangu/api/user' and method.lower() == 'post':
            fields = user_view_post + link.fields
            description = '创建user'
        if link.url == f'/pangu/api/user' and method.lower() == 'put':
            fields = user_view_put + link.fields
            description = '修改user'
        if link.url == f'/pangu/api/user' and method.lower() == 'delete':
            fields = user_view_delete + link.fields
            description = '删除user'

        return coreapi.Link(
            url=link.url,
            action=link.action,
            encoding=link.encoding,
            fields=fields,
            description=description)

