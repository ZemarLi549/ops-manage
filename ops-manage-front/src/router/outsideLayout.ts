import type { RouteRecordRaw } from 'vue-router';
import { LOGIN_NAME } from '@/router/constant';

/**
 * layout布局之外的路由
 */
export const LoginRoute: Array<RouteRecordRaw> = [
  {
    path: '/login',
    name: LOGIN_NAME,
    component: () => import(/* webpackChunkName: "login" */ '@/views/login/index.vue'),
    meta: {
      title: '登录',
    },
  },
  {
    path: '/alarmedit',
    name: 'alarmedit',
    meta: {
      title: '指纹处理',
      hideInMenu: true,
    },
    component: () => import('@/views/alarm/alarmedit/index.vue'),
  },
  {
    path: '/alarmdetail',
    name: 'alarmdetail',
    component: () => import('@/views/alarm/alarmdetail/index.vue'),
    meta: {
      title: '指纹详情',
    },
  },
];

export default LoginRoute;
