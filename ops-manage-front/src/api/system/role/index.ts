import { request } from '@/utils/request';
// import type { BaseResponse } from '@/utils/request';
import Api from '@/core/permission/modules/sys/role';

export function getRoleInfo(query: { roleId: number }) {
  return request<API.RoleInfoResult>({
    url: Api.info,
    method: 'get',
    params: query,
  });
}

export function getRoleList(data?: API.PageParams) {
  return request<API.RoleListResult>({
    url: Api.api,
    method: 'get',
    data,
  });
}

export function getRoleListByPage(query: API.PageParams) {
  return request(
    {
      url: Api.api,
      method: 'get',
      params: query,
    },
    { isGetDataDirectly: false },
  );
}

export function createRole(data: API.CreateRoleParams) {
  return request(
    {
      url: Api.api,
      method: 'put',
      data,
    },
    {
      successMsg: '创建角色成功',
    },
  );
}

export function updateRole(data: API.UpdateRoleParams) {
  return request(
    {
      url: Api.api,
      method: 'put',
      data,
    },
    {
      successMsg: '更新角色成功',
    },
  );
}

export function deleteRole(data: { roleIds: number[] }) {
  return request(
    {
      url: Api.api,
      method: 'delete',
      data,
    },
    {
      successMsg: '删除角色成功',
    },
  );
}
