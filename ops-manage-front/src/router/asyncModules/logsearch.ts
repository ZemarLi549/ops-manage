/**
 * system module
 */
export default {
  'views/log/source': () => import('@/views/logsearch/datasource/index.vue'),
  'views/log/appconfig': () => import('@/views/logsearch/appconfig/index.vue'),
  'views/log/gateconfig': () => import('@/views/logsearch/gateconfig/index.vue'),
  'views/log/autocoll': () => import('@/views/logsearch/autocollect/index.vue'),
  'views/log/component': () => import('@/views/logsearch/component/index.vue'),
  'views/log/gatepass': () => import('@/views/logsearch/gatepass/index.vue'),
  'views/log/apppass': () => import('@/views/logsearch/apppass/index.vue'),
} as const;
