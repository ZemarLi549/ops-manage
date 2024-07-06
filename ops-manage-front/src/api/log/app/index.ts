import { request } from '@/utils/request';
// import type { BaseResponse } from '@/utils/request';
import Api from '@/core/permission/modules/log/appconfig';

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
export function getAppfilter(data: any) {
  return request(
    {
      url: 'log/appfilter',
      method: 'get',
      params: data,
    },
    {
      isGetDataDirectly: false,
    },
  );
}

export function getAppList(data: any) {
  return request(
    {
      url: 'log/applist',
      method: 'get',
      params: data,
    },
    {
      isGetDataDirectly: false,
    },
  );
}
// 应用日志查询
export function appQuery(data: any) {
  return request(
    {
      url: 'log/appquery',
      method: 'post',
      data,
    },
    {
      isGetDataDirectly: false,
    },
  );
}
// 应用日志hisgram查询
export function appHisGram(data: any) {
  return request(
    {
      url: 'log/apphisgram',
      method: 'post',
      data,
    },
    {
      isGetDataDirectly: false,
    },
  );
}
// 应用日志hisgram查询
export function appLocate(data: any) {
  return request(
    {
      url: 'log/applocate',
      method: 'post',
      data,
    },
    {
      isGetDataDirectly: false,
    },
  );
}
