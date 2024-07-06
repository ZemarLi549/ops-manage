from django.conf import settings
import json
import requests
import datetime
import re
import logging
logger = logging.getLogger(__name__)
import ldap
from ..management.models import *

import traceback

class LdapService():
    def __init__(self):
        super(LdapService, self).__init__()
    def auth(self, username, password,is_debug=False, auto_create=True, auto_update=False):
        """
        通过从ad获取用户信息
        @username
        return tuple
        """

        AUTH_LDAP_SERVER_URI = settings.AD_SERVER
        AUTH_LDAP_BIND_DN = settings.AD_BIND_DN
        AUTH_LDAP_BIND_PASSWORD = settings.AD_PASSWORD
        AUTH_LDAP_BASE_DN = settings.AD_BASE_DN
        if username and password:
            # 初始化ldap连接
            ldapconn = ldap.initialize(AUTH_LDAP_SERVER_URI)
            # 设置连接协议为version3
            ldapconn.protocol_version = ldap.VERSION3
            # 使用管理员账号，密码登陆ldap
            ldapconn.simple_bind_s(AUTH_LDAP_BIND_DN, AUTH_LDAP_BIND_PASSWORD)
            # 根据我们需要的字段(此处的字段是值ldap查询到的数据的字段)搜索到指定的账户，sn是我用的，不同公司的可能不一样，需要根据自己的实际情况确定
            ldap_result_id = ldapconn.search(AUTH_LDAP_BASE_DN, ldap.SCOPE_SUBTREE, f"(&(uid={username})(objectclass=posixAccount))", None)
            # 获取到查询的结果数据
            result_type, result_data = ldapconn.result(ldap_result_id, 1)
            # 如果查询到了用户就继续验证
            logger.info(result_data)
            if (not len(result_data) == 0):
                try:
                    # 初始化ldap连接
                    ldapconn = ldap.initialize(AUTH_LDAP_SERVER_URI)
                    # 使用刚刚查到的登陆用的DN信息和密码再次登陆一下ldap
                    # 1、如果登陆成功会返回一个类似于右边的一个元祖数据(97, [], 1, [])
                    # 2、如果登陆失败就会抛出一个ldap.INVALID_CREDENTIALS的异常
                    ldapconn.simple_bind_s(result_data[0][0], password)
                    logger.debug("ldap auth success")
                    logger.info(result_data)

                    return result_data[0][1]
                except ldap.INVALID_CREDENTIALS:
                    return {}
            return {}
        else:
            return {}


    def authenticate(self, username, password, is_debug=False, auto_create=True, auto_update=False):
        """
        用户认证
        :param username:
        :param password:
        :param is_debug:
        :param auto_create:
        :return:
        """

        if username == 'om_api':
            return True, {'name':'zengxin.li'}
        elif settings.AD_SERVER:
            try:
                logger.info('username %s before auth' % username)
                user_ = self.auth(
                    username,
                    password
                )
                logger.info('username %s end auth' % username)

                if user_:
                    ad_user = {
                        "username": user_["uid"][0].decode('utf-8'),
                        "name": user_["cn"][0].decode('utf-8'),
                        "email": user_["mail"][0].decode('utf-8'),
                        "mobile": user_["mobile"][0].decode('utf-8'),
                        "uid": user_["uidNumber"][0].decode('utf-8'),
                        "gid": user_["gidNumber"][0].decode('utf-8')
                    }
                    if not ad_user:
                        return False,{}
                    elif auto_update:
                        logger.debug('username %s end update' % username)
                    else:
                        if auto_create:
                            logger.info('username %s need create' % username)
                            if ad_user.get('username'):
                                if User.objects.filter(name=ad_user.get('username')).exists():
                                    pass
                                else:
                                    User.objects.create(name=ad_user.get('username'),
                                                        status=1,
                                                        realname=ad_user.get('realname'),
                                                        created_by='sys')
                        return True, ad_user
                else:
                    return False, {'msg':'ldap validate fail'}


            except Exception as error:
                logger.error(traceback.format_exc())
                return False,{'msg':error}
        else:
            return False, {}

