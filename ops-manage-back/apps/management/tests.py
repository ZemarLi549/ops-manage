from django.test import TestCase

# Create your tests here.
# @swagger_auto_schema(
    #     operation_description="resourceapiview post",
    #     request_body=openapi.Schema(
    #         type=openapi.TYPE_OBJECT,
    #         required=['id', "name"],
    #         properties={
    #             'id': openapi.Schema(type=openapi.TYPE_INTEGER),
    #             'name': openapi.Schema(type=openapi.TYPE_STRING)
    #
    #         },
    #     ),
    #     security=[]
    # )

# test_param = openapi.Parameter("id", openapi.IN_QUERY, description="test manual param",
#                                    type=openapi.TYPE_INTEGER)





# class ResourceView(APIView):
#     """
#     """
#     # schema =  ResourceViewSchema()
#     renderer_classes = [MyJSONRenderer]
#
#
#     @swagger_auto_schema(operation_summary=' 资源查询',
#                         operation_description=' 资源get',
#                          query_serializer= ResourceGetForm)
#     @try_catch
#     def get(self, request):
#         query_params = request.query_params.dict()
#         logger.info("params:%s", query_params)
#         name = query_params.get('name', None)
#         id = query_params.get('id', None)
#         login_user = request.data.get('login_user', 'sys')
#         description = query_params.get('description', None)
#         res_type = query_params.get('res_type', None)
#         code = query_params.get('code', None)
#         parent_id = query_params.get('parent_id', None)
#         search_type = query_params.get('search_type', 'name') # id, name
#         search_value = query_params.get('search_value')
#         page_no = int(query_params.get('page_no', '1'))
#         page_size = int(query_params.get('page_size', '10'))
#
#         if page_no <= 0 or page_size <= 0 or page_size > 5000:
#             raise ValueError(f'page_no{page_no} or page_size{page_size} is not in valid range.')
#
#         resource_query_sql = 'select id, name, updated_at, updated_by, created_at, created_by ' \
#                             ' from om_resource '
#         condition_sql = ' where '
#         params = []
#
#         if name:
#             condition_sql += ' and (instr(name,%s)) '
#             params.append("{}".format(name))
#         if description:
#             condition_sql += ' and (instr(description,%s)) '
#             params.append("{}".format(description))
#         if res_type:
#             condition_sql += ' and (res_type = %s) '
#             params.append("{}".format(res_type))
#         if code:
#             condition_sql += ' and (code = %s) '
#             params.append("{}".format(code))
#         if parent_id:
#             condition_sql += ' and (parent_id = %s) '
#             params.append("{}".format(parent_id))
#         if id:
#             condition_sql += ' and (id = %s) '
#             params.append("{}".format(id))
#         resource_list = dict_query(resource_query_sql + condition_sql + ' order by updated_at desc, id desc limit %s,%s',
#                                   [*params, (page_no - 1) * page_size, page_size])
#
#         if not resource_list:
#             return Response({'status': 'success', 'message': 'OK', 'data': [], },
#                             http_status.HTTP_200_OK)
#
#
#
#         return Response({'status': 'success', 'message': 'OK', 'data': resource_list},
#                         http_status.HTTP_200_OK)
#
#     @swagger_auto_schema(operation_summary=' 资源新建',
#                          operation_description='传递id,name,res_type',
#                          request_body=ResourceForm)
#     @try_catch
#     def post(self, request):
#         logger.info("request.data:%s", request.data)
#         name = request.data.get('name', None)
#         res_type = request.data.get('res_type', None)
#         login_user = request.data.get('login_user', 'sys')
#         code = request.data.get('code', '')
#         parent_id = request.data.get('parent_id', 0)
#         description = request.data.get('description', 1)
#         if not name:
#             raise KeyError('name missing in request.')
#         if not res_type:
#             raise KeyError('res_type missing in request.')
#         if not Resource.objects.filter(name=name).exists():
#              Resource.objects.create(name=name,
#                                     description=description,
#                                     res_type=res_type,
#                                     code=code,
#                                     parent_id=parent_id,
#                                     created_by=login_user)
#              return Response({'status': 'success', 'message': 'OK'},
#                             http_status.HTTP_200_OK)
#         else:
#              logger.error("resource(%s) alread exists.", name)
#              return Response({'status': 'fail', 'message': f"resource({name}) already exists."},
#                             http_status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#     @swagger_auto_schema(operation_summary=' 资源修改',
#                          operation_description=' 资源put',
#                          query_serializer=PutBaseForm)
#     @try_catch
#     def put(self, request):
#         logger.info("request.data:%s", request.data)
#         login_user = request.data.get('login_user', 'sys')
#         description = request.data.get('description', None)
#         resource_id = request.data.get('id', None)
#
#
#         if not resource_id:
#             raise KeyError('resource id missing in request.')
#         resource =  Resource.objects.get(pk=resource_id)
#         now = get_datetime_now()
#         other_fields = [
#             'name',
#             'description',
#             'res_type',
#             'code',
#             'parent_id',
#         ]
#         for field in other_fields:
#             if field in request.data:
#                 setattr(resource, field, request.data.get(field))
#
#         resource.updated_by = login_user
#         resource.updated_at = now
#         resource.save()
#         return Response({'status': 'success', 'message': 'OK'},
#                             http_status.HTTP_200_OK)
#
#     @swagger_auto_schema(operation_summary=' 资源删除',
#                          operation_description=' 资源del',
#                          query_serializer=DeleteBaseForm)
#     @try_catch
#     def delete(self, request):
#         query_params = request.query_params.dict()
#         logger.info("params:%s", query_params)
#         resource_id = query_params.get('id', None)
#         login_user = request.data.get('login_user', 'sys')
#
#         if not resource_id:
#             raise KeyError('resource_id missing in request.')
#         resource_id = int(resource_id)
#         now = get_datetime_now()
#
#
#         if  Resource.objects.filter(id=resource_id).exists():
#             ex = Execution()
#             # for key, val in ex.load_plugins("management","models","resources", cls=None):
#             #    logger.info(key,val)
#             funcs = ex.load_plugins("management", "models", "resource")
#             for table,table_obj in funcs.items():
#                 if table_obj.objects.filter(resource_id=resource_id).exists():
#                     logger.error("resource:(%d) is related to %s.", (resource_id,table))
#                     return Response({'status': 'fail', 'message': f"resource({resource_id}) is related to {table}."},
#                                     http_status.HTTP_500_INTERNAL_SERVER_ERROR)
#
#             resource =  Resource.objects.filter(id=resource_id)
#             resource_copy = resource[0].as_dict()
#             resource.delete(pk=resource_id)
#
#             return Response({'status': 'success', 'message': 'OK'},
#                             http_status.HTTP_200_OK)
#         else:
#             logger.error("resource(%d) does not exist.", resource_id)
#             return Response({'status': 'fail', 'message': f"resource({resource_id}) does not exist."},
#                             http_status.HTTP_500_INTERNAL_SERVER_ERROR)