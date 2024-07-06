import { request } from '@/utils/request';
export function getFunc(url: string, param: {}) {
  return request<API.CommonInfo>(
    {
      url,
      method: 'get',
      params: param,
    },
    {
      isGetDataDirectly: false,
    },
  );
}
