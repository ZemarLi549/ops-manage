import { request } from '@/utils/request';

/**
 * @description 登录
 * @param {LoginParams} data
 * @returns
 */
export function hostTable(data: any) {
  return request(
    {
      url: 'log/hosttable',
      method: 'post',
      data,
    },
    {
      isGetDataDirectly: false,
    },
  );
}

//状态码分布
export function statusLine(data: any) {
  return request(
    {
      url: 'log/statusline',
      method: 'post',
      data,
    },
    {
      isGetDataDirectly: false,
    },
  );
}

//响应时间分布
export function reqAllLine(data: any) {
  return request(
    {
      url: 'log/reqallline',
      method: 'post',
      data,
    },
    {
      isGetDataDirectly: false,
    },
  );
}

//流入流出量
export function netAllLine(data: any) {
  return request(
    {
      url: 'log/netallline',
      method: 'post',
      data,
    },
    {
      isGetDataDirectly: false,
    },
  );
}
//流入流出量
export function methodStLine(data: any) {
  return request(
    {
      url: 'log/methodstline',
      method: 'post',
      data,
    },
    {
      isGetDataDirectly: false,
    },
  );
}

//响应时间占比
export function respPie(data: any) {
  return request(
    {
      url: 'log/resppie',
      method: 'post',
      data,
    },
    {
      isGetDataDirectly: false,
    },
  );
}
//状态码占比 请求类型占比
export function commonPie(data: any) {
  return request(
    {
      url: 'log/commonpie',
      method: 'post',
      data,
    },
    {
      isGetDataDirectly: false,
    },
  );
}

//five nine resp live
export function fiveNineResp(data: any) {
  return request(
    {
      url: 'log/fivenine',
      method: 'post',
      data,
    },
    {
      isGetDataDirectly: false,
    },
  );
}
// uv clientIp占比
export function clientIpPie(data: any) {
  return request(
    {
      url: 'log/clientpie',
      method: 'post',
      data,
    },
    {
      isGetDataDirectly: false,
    },
  );
}

// 网关日志查询
export function gateQuery(data: any) {
  return request(
    {
      url: 'log/gatequery',
      method: 'post',
      data,
    },
    {
      isGetDataDirectly: false,
    },
  );
}
