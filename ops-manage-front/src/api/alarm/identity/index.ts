import { request } from '@/utils/request';
// import type { BaseResponse } from '@/utils/request';
import Api from '@/core/permission/modules/alarm/alarmidentity';

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

export function getDataInfo(query: any) {
  return request(
    {
      url: Api.info,
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

export function postData(data: any) {
  return request(
    {
      url: Api.api,
      method: 'post',
      data,
    },
    {
      successMsg: '操作成功',
      isGetDataDirectly: false,
    },
  );
}
export function alarmSimilarData(data: any) {
  return request(
    {
      url: Api.alarmsimilar,
      method: 'post',
      data,
    },
    {
      isGetDataDirectly: false,
    },
  );
}

export function alarmExistData(data: any) {
  return request(
    {
      url: Api.alarmexist,
      method: 'post',
      data,
    },
    {
      isGetDataDirectly: false,
    },
  );
}
export function alarmQueryData(data: any) {
  return request(
    {
      url: Api.alarm_query,
      method: 'post',
      data,
    },
    {
      isGetDataDirectly: false,
    },
  );
}
export function alarmHisGramData(data: any) {
  return request(
    {
      url: Api.alarm_hisgram,
      method: 'post',
      data,
    },
    {
      isGetDataDirectly: false,
    },
  );
}

export function alarmLocateData(data: any) {
  return request(
    {
      url: Api.alarm_locate,
      method: 'post',
      data,
    },
    {
      isGetDataDirectly: false,
    },
  );
}
