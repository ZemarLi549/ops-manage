import type { RouteRecordRaw } from 'vue-router';
const routes: Array<RouteRecordRaw> = [
  {
    path: '/home',
    name: 'home',
    meta: {
      title: '简介',
      icon: 'tuisong',
    },
    component: () => import('@/views/home/index.vue'),
  },

  {
    path: '/log',
    name: 'log',
    meta: {
      title: '日志系统',
      icon: 'xinxixiaoyan',
    },
    children: [
      {
        path: '/applogs',
        name: 'applogs',
        meta: {
          title: '服务日志',
          icon: 'rizhi-2',
          keepAlive: true,
        },
        component: () => import('@/views/logsearch/applogs/index.vue'),
      },

      {
        path: '/gatelogs',
        name: 'gatelogs',
        meta: {
          title: '网关日志',
          icon: 'jueceyinqing',
          keepAlive: true,
        },
        component: () => import('@/views/logsearch/gatelogs/index.vue'),
      },
      {
        path: '/gateall',
        name: 'gateall',
        meta: {
          title: '网关总览',
          icon: 'gateall',
          keepAlive: true,
        },
        component: () => import('@/views/logsearch/gateall/index.vue'),
      },
    ],
  },
  {
    path: '/alarm',
    name: 'alarm',
    meta: {
      title: '监控系统',
      icon: 'jingbao',
    },
    children: [
      {
        path: '/alarmsetting',
        name: 'alarmsetting',
        meta: {
          title: '告警配置',
          icon: 'xitongcanshupeizhi',
        },
        children: [
          {
            path: '/alarmusers',
            name: 'alarmusers',
            meta: {
              title: '告警联系人',
              keepAlive: true,
            },
            component: () => import('@/views/alarm/alarmuser/index.vue'),
          },
          {
            path: '/alarmconf',
            name: 'alarmconf',
            meta: {
              title: '告警方式',
              // keepAlive: true,
            },
            component: () => import('@/views/alarm/alarmconfig/index.vue'),
          },
          {
            path: '/alarmrules',
            name: 'alarmrules',
            meta: {
              title: '指纹规则',
              keepAlive: true,
            },
            component: () => import('@/views/alarm/alarmrule/index.vue'),
          },
          {
            path: '/alarmblack',
            name: 'alarmblack',
            meta: {
              title: '告警黑名单',
              keepAlive: true,
            },
            component: () => import('@/views/alarm/alarmblack/index.vue'),
          },
        ],
      },
      {
        path: '/alarmidentity',
        name: 'alarmidentity',
        meta: {
          title: '指纹展示',
          keepAlive: true,
          icon: 'identity',
        },
        component: () => import('@/views/alarm/alarmidentity/index.vue'),
      },
      {
        path: '/identityhis',
        name: 'identityhis',
        meta: {
          title: '指纹历史',
          keepAlive: true,
          icon: 'shanchu',
        },
        component: () => import('@/views/alarm/identityhis/index.vue'),
      },
      {
        path: '/alarmlog',
        name: 'alarmlog',
        meta: {
          title: '告警查询',
          keepAlive: true,
          icon: 'tixing-jinggao',
        },
        component: () => import('@/views/alarm/alarmlog/index.vue'),
      },
    ],
  },
];

export default routes;
