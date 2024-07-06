# -*- coding: utf-8 -*-
import json

from ..common.services import LdapService
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as http_status
import requests
from django.shortcuts import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from apps.common.renderers import MyJSONRenderer
from ..management.forms import LoginPostForm,LogoutForm,TokenForm
from drf_yasg.utils import swagger_auto_schema
from apps.common.try_catch import try_catch
from rest_framework import status as http_status
import logging
from apps.management.models import User
from apps.common.verify import generate_jwt,verify_jwt
from apps.common.tools import encrypt,decrypt

import base64
from apps.common.redisclient import get_code_ls, RedisClient
logger = logging.getLogger(__name__)
# Create your views here.


from django.shortcuts import render
from django.views.generic import View
from captcha.views import CaptchaStore,captcha_image
from django.http import HttpResponseRedirect
from django.http import HttpResponse
import json
from lxml import etree


# 验证验证码
def jarge_captcha(captchaStr, captchaHashkey):
    if captchaStr and captchaHashkey:
        try:
            # 获取根据hashkey获取数据库中的response值
            get_captcha = CaptchaStore.objects.get(hashkey=captchaHashkey)
            print(get_captcha.response)
            if get_captcha.response == captchaStr.lower():  # 如果验证码匹配
                return True
        except:
            return False
    else:
        return False
class LoginAuth(MiddlewareMixin):

    def process_request(self, request):
        full_path = request.get_full_path()
        # print('>>>>>>>>>>>>>>>>inin',full_path)

        flag = True
        for url in settings.WHITE_URL_LIST:
            if url in full_path:
                flag = False
                break

        if flag:
            token = request.headers.get("Authorization", '')
            logger.info(token)
            if token:
                _, payload = verify_jwt(token)
                if not _:
                    res = HttpResponse(json.dumps({'code': 401, 'message': 'token error please login'}),
                                       content_type="application/json", )
                    res.status_code = http_status.HTTP_401_UNAUTHORIZED
                    return res
                else:
                    setattr(request, "username", payload.get("username", ""))
                    setattr(request, "realname", payload.get("realname", ""))
                    setattr(request, "loginIp", payload.get("loginIp", ""))
            else:
                if request.headers.get("ApiToken", None) in settings.OPS_TOKEN.split(','):
                    pass
                else:
                    res = HttpResponse(json.dumps({'code': 401, 'message': 'token not exists please login'}),
                                       content_type="application/json", )
                    res.status_code = http_status.HTTP_401_UNAUTHORIZED
                    return res





class CapthaGetView(APIView):

    @try_catch
    def get(self, request):
        width = request.data.get('width', 100)
        height = request.data.get('height', 50)
        # settings.CAPTCHA_IMAGE_SIZE = (width,height)
        hashkey = CaptchaStore.generate_key()
        try:
            # 获取图片id
            # id_ = CaptchaStore.objects.filter(hashkey=hashkey).first().id
            imgage = captcha_image(request, hashkey)
            # 将图片转换为base64
            image_base = 'data:image/png;base64,%s' % base64.b64encode(imgage.content).decode('utf-8')
            captcha = {"id": hashkey, "img": image_base}
            # 批量删除过期验证码
            CaptchaStore.remove_expired()
        except Exception as e:
            logger.error(f'captche error:{e}')
            captcha = {}
        return  Response({'code': 200, 'message': 'OK', 'data': captcha},
                            http_status.HTTP_200_OK)

class LoginView(APIView):
    renderer_classes = [MyJSONRenderer]
    @swagger_auto_schema(operation_summary='用户登陆',
                         operation_description='ldap登陆',
                         request_body=LoginPostForm)
    @try_catch
    def post(self, request):
        logger.info("request.data:%s", request.data)
        is_auth = False
        data = {}

        username = request.data.get('username', None)
        captchaId = request.data.get('captchaId', '')
        verifyCode = request.data.get('verifyCode', '')
        password = request.data.get('password', None)
        ticket = request.data.get('ticket', '')
        if not ticket:
            pass
        else:
            print('ticket>>>',ticket)
            resp_sso = requests.get(f'{settings.SSO_VALIDATE}&ticket={ticket}',verify=False)
            print('resp_sso>>>>',resp_sso.text)
            if resp_sso.status_code == 200:
                # 获取CAS响应的XML内容
                xml_content = resp_sso.text
                # 解析XML内容
                root = etree.fromstring(xml_content)

                # 获取用户信息
                username = root.find(".//cas:user", namespaces={"cas": "http://www.yale.edu/tp/cas"}).text
                attributes = root.find(".//cas:attributes", namespaces={"cas": "http://www.yale.edu/tp/cas"})
                realname = attributes.find(".//cas:userName", namespaces={"cas": "http://www.yale.edu/tp/cas"}).text
                # print(username, realname)
                if not User.objects.filter(name=username).exists():
                    User.objects.create(name=username,
                                        password=encrypt('xunfei', settings.RELEASE_KEY),
                                        realname=realname,
                                        status=1,
                                        created_by='sys')
                # for attribute in attributes:
                #     print(attribute.tag, ":", attribute.text)
                # username = 'zengxin.li'
                # realname = '李增鑫'
                record_ = {
                    "username": username,
                    "realname": realname,
                    "loginIp": request.META['REMOTE_ADDR'],
                }
                token = generate_jwt(record_, settings.TOKEN_AGE)
                data["token"] = token
                return Response({'code': 200, 'message': 'OK', 'data': data, },
                                http_status.HTTP_200_OK)
            else:
                return Response({'code': 500, 'message': 'cas账户或密码错误'},
                                http_status.HTTP_401_UNAUTHORIZED)

        if not username:
            raise KeyError('username missing in request.')
        if not password:
            raise KeyError('pwd missing in request.')
        # if not jarge_captcha(verifyCode, captchaId):
        #     return Response({'code': 500, 'message': '验证码错误'},
        #                     http_status.HTTP_500_INTERNAL_SERVER_ERROR)
        # is_auth,data = LdapService().authenticate(username,password)

        user_list = User.objects.filter(name=username,status=1).values('name','password','realname')
        flag_ = False
        for user in user_list:
            if decrypt(user['password'],settings.RELEASE_KEY)==password:
                flag_ = True
                data['username'] = user['name']
                data['realname'] = user['realname']
                break


        if is_auth or flag_:
            record_ = {
                "username":username,
                "realname":data.get('realname',''),
                "loginIp":request.META['REMOTE_ADDR'],
            }
            token=generate_jwt(record_,settings.TOKEN_AGE)
            data["token"]=token
            return Response({'code': 200, 'message': 'OK', 'data': data, },
                            http_status.HTTP_200_OK)
        else:
            return Response({'code': 500, 'message': '账户或密码错误'},
                            http_status.HTTP_401_UNAUTHORIZED)

from django.shortcuts import redirect
class LogoutView(APIView):

    @try_catch
    def post(self, request):
        logger.info(f'{request.username} logout')
        token=request.headers.get("x-token")

        try:
            r = RedisClient('dbmonitor').client
            r.delete(f'getcode:{request.username}')
        except Exception as e:
            logger.error(f'del cache error:{e}')
        # return redirect('https://ssoqxb.iflytek.com:8443/sso/logout?service=http://127.0.0.1:8098/login/')
        return Response({'code': 200, 'message': 'OK', 'data': ''},
                        http_status.HTTP_200_OK)


class TokenView(APIView):
    renderer_classes = [MyJSONRenderer]

    @try_catch
    def get(self, request):
        tk = request.query_params['user_token']
        user_token = request.session.get('user_token')
        if user_token and user_token==tk:
            return Response({'status': 'sucess', 'message': 'OK'},
                            http_status.HTTP_200_OK)
        else:
            return Response({'code': 401, 'message': 'login session expired'},
                            http_status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserRegView(APIView):
    """
    """
    @try_catch
    def post(self, request):
        logger.info("request.data:%s", request.data)
        name = request.data.get('regUser', None)
        realname = request.data.get('realname', '')
        password = request.data.get('regPwd', '')
        status = request.data.get('status', 1)
        if (not name and password):
            raise KeyError('name pwd missing in request.')

        if not User.objects.filter(name=name).exists():
            User.objects.create(name=name,
                                password=encrypt(password,settings.RELEASE_KEY),
                                realname=realname,
                                status=status,
                                created_by=name)
            return Response({'code': 200, 'message': 'OK'},
                            http_status.HTTP_200_OK)
        else:
            logger.error("user(%s) alread exists.", name)
            return Response({'code': 500, 'message': f"user({name}) already exists."},
                            http_status.HTTP_500_INTERNAL_SERVER_ERROR)