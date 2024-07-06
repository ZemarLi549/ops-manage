import { request } from '@/utils/request';
// import type { BaseResponse } from '@/utils/request';
import Api from '@/core/permission/modules/alarm/alarmcomment';

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

export function putDataListByPage(query: API.PageParams) {
  return request(
    {
      url: Api.putcmt,
      method: 'get',
      params: query,
    },
    { isGetDataDirectly: false },
  );
}

export function batchcreateData(data: any) {
  return request(
    {
      url: Api.batch,
      method: 'post',
      data,
    },
    {
      successMsg: '批量评论成功',
      isGetDataDirectly: false,
    },
  );
}

export function createData(data: any) {
  return request(
    {
      url: Api.putcmt,
      method: 'post',
      data,
    },
    {
      // successMsg: '评论成功',
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
