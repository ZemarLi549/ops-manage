import type { RouteRecordRaw } from 'vue-router';
import RouterView from '@/layout/routerView/index.vue';

const routes: Array<RouteRecordRaw> = [
  {
    path: 'https://code.iflytek.com/osc/_source/zxli22/ops-manage-front/-/code/',
    name: 'https://code.iflytek.com/osc/_source/zxli22/ops-manage-front/-/code/',
    component: RouterView,
    meta: {
      title: 'git代码地址',
      icon: 'icon-externa-link',
    },
  },
];

export default routes;
