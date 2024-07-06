import { request } from '@/utils/request';
import Api from '@/core/permission/modules/sys/user';

export function getUserListPage(data: any) {
  return request<any>(
    {
      url: Api.api,
      method: 'get',
      params: data,
    },
    { isGetDataDirectly: false },
  );
}

export function createUser(data: API.CreateUserParams) {
  return request(
    {
      url: Api.api,
      method: 'post',
      data,
    },
    {
      successMsg: '创建用户成功',
    },
  );
}

export function getUserInfo(query: { userId: number }) {
  return request<API.AdminUserInfo>({
    url: Api.info,
    method: 'get',
    params: query,
  });
}

export function updateUser(data: API.UpdateAdminInfoParams) {
  return request(
    {
      url: Api.api,
      method: 'put',
      data,
    },
    {
      successMsg: '修改用户成功',
    },
  );
}

export function updateUserPassword(data: API.UpdateAdminUserPassword) {
  return request(
    {
      url: Api.api,
      method: 'put',
      data,
    },
    {
      successMsg: '操作成功',
    },
  );
}

export function deleteUsers(data: { userIds: number[] }) {
  return request({
    url: Api.api,
    method: 'delete',
    data,
  });
}
