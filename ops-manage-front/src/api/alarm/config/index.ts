import { request } from '@/utils/request';
// import type { BaseResponse } from '@/utils/request';
import Api from '@/core/permission/modules/alarm/alarmconfig';

export function getDataListByPage(query: API.PageParams) {
  return request(
    {
      url: Api.api,
      method: 'get',
      params: query,
    },
    { isGetDataDirectly: false },
  );
}

export function createData(data: any) {
  return request(
    {
      url: Api.api,
      method: 'put',
      data,
    },
    {
      successMsg: '创建成功',
      isGetDataDirectly: false,
    },
  );
}

export function updateData(data: any) {
  return request(
    {
      url: Api.api,
      method: 'put',
      data,
    },
    {
      successMsg: '更新成功',
    },
  );
}

export function deleteData(data: any) {
  return request(
    {
      url: Api.api,
      method: 'delete',
      data,
    },
    {
      successMsg: '删除成功',
      isGetDataDirectly: false,
    },
  );
}
