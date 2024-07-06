# -*-coding:utf-8-*-
import logging
import inspect
from datetime import datetime
from functools import wraps
from django.shortcuts import HttpResponse
from rest_framework.response import Response
from rest_framework import status
import json
import traceback
from apps.common.redisclient import get_code_ls
logger = logging.getLogger(__name__)


def try_catch(func):
    func_name = func.__qualname__

    @wraps(func)
    def _do_try_catch(*args, **params):
        try:
            beg_time = datetime.now()
            back = func(*args, **params)
            end_time = datetime.now()
            time_dtt = str((end_time - beg_time).total_seconds())
            logger.info('func: %s, cost:%s s' % (func_name, time_dtt))
            return back
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error("Function_Name:[%s] err:[%s]" % (func_name, e))
            return_data = {
                'data': [],
                'status': 'fail',
                'message': str(e)
            }
            args_dict = inspect.getcallargs(func, *args)
            for k, v in list(params.items()): args_dict.setdefault(k, v)
            if "self" in args_dict: del args_dict["self"]
            if "request" in args_dict: del args_dict["request"]
            if hasattr(e, "code") or hasattr(e, "status_code"):
                if hasattr(e, "code"):
                    e.status_code = e.code

                return Response(str(e), e.status_code)

            return Response(return_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return _do_try_catch
def power_decorator(codeList,powerType='or'):
    '''
    :param codeList:#为空时不用拦截，仅仅不允许调接口
    :param powerType: 默认or,任意，当为and时，apitoken或者username关联当角色必须有codeList所有权限
    :return:
    '''
    codeList = [item.strip() for item in codeList]
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # args_dict = inspect.getcallargs(func, *args)
            # request = args_dict.get('request')

            res = HttpResponse(json.dumps({
                'status': 'fail',
                'message': f'您没有{codeList} powerType:{powerType}权限'
            }),
                content_type="application/json")
            res.status_code = 200

            request = args[1]
            code_ls = []
            username = request.username if hasattr(request, 'username') else ''
            # 走auth全局固定apitoken，不动态了
            # ApiToken = request.headers.get("ApiToken", '')
            # if ApiToken:#调接口模式
            #     menu_all = get_token_ls(ApiToken)
            if username:#页面访问模式
                menu_all = get_code_ls(username)
            else:
                return res
            for item in menu_all:
                if item['type'] == 2:
                    code_ls.extend(item['perms'].split(','))
            # if ApiToken or codeList:#为空时不用拦截，仅仅不允许调接口
            if codeList:
                if powerType == 'or':
                    flag_pass = False
                    for item in codeList:

                        if item in code_ls:
                            flag_pass = True
                            break
                    if not flag_pass:
                        return res
                else:
                    for item in codeList:
                        if not item in code_ls:
                            return res
            return func(*args, **kwargs)

        return wrapper

    return decorator