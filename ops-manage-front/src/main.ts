// with polyfills
import 'core-js/stable';
import 'regenerator-runtime/runtime';
import 'ant-design-vue/dist/antd.css';
import { createApp } from 'vue';

import { message } from 'ant-design-vue';
import App from './App.vue';
import { setupRouter } from './router';
import { setupStore } from '@/store';
import { setupI18n } from '@/locales';
import filter from '@/plugins/filter';
import { setupAntd, setupAssets, setupGlobalMethods, setupCustomComponents } from '@/plugins';
// const { mockXHR } = require('./mock');

// if (process.env.ENV === 'development') {
// mockXHR();
// }

const app = createApp(App);

app.config.globalProperties.$filters = {
  fmtTime(value) {
    return filter.fmtTime(value);
  },
  addZero(value) {
    return filter.addZero(value);
  },
  sizeType(value) {
    return filter.sizeType(value);
  },
  aliyunEcsMemory(value) {
    if (value === 0) return '0';
    const k = 1024,
      sizes = ['MB', 'GB', 'TB'],
      i = Math.floor(Math.log(value) / Math.log(k));
    return `${(value / Math.pow(k, i)).toPrecision(3)} ${sizes[i]}`;
  },
};

app.provide('$message', message);

function setupPlugins() {
  // 注册全局常用的ant-design-vue组件
  setupAntd(app);
  // 引入静态资源
  setupAssets();
  // 注册全局自定义组件,如：<svg-icon />
  setupCustomComponents(app);
  // 注册全局方法，如：app.config.globalProperties.$message = message
  setupGlobalMethods(app);
}

async function setupApp() {
  // 挂载vuex状态管理
  setupStore(app);
  // Multilingual configuration
  // Asynchronous case: language files may be obtained from the server side
  await setupI18n(app);
  // 挂载路由
  await setupRouter(app);

  app.mount('#app');
}

setupPlugins();

setupApp();
