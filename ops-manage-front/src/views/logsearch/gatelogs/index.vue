<template>
  <div class="screen">
    <a-row :gutter="4">
      <FilterForm @searchClick="searchClick" />
    </a-row>
    <div
      style="
        width: 100%;
        width: 100%;
        padding: 10px 0;
        white-space: nowrap;
        overflow-x: scroll;
        white-space: nowrap;
        overflow-x: scroll;
      "
    >
      <a-pagination
        :page-size="state.size"
        :show-total="(total) => `共 ${state.total} 条数据`"
        :current="state.page"
        :total="state.total"
        show-less-items
        :show-size-changer="false"
        show-quick-jumper
        align="left"
        @change="onChange"
      >
        <template #buildOptionText="props">
          <span v-if="props.value !== '50'">{{ props.value }}条/页</span>
          <span v-if="props.value === '50'">全部</span>
        </template>
      </a-pagination>
    </div>
    <a-table
      row-key="_id"
      size="default"
      :scroll="{ x: 1000 }"
      :columns="columns"
      :data-source="state.dataSource"
      :loading="state.tableLoading"
      :pagination="false"
      @change="handleTableChange"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.dataIndex === 'message'">
          <div style="max-height: 50px; overflow-y: scroll">
            {{
              record.message.request_method +
              '    ' +
              record.message.uri +
              (record.message?.args ? '?' + record.message?.args : '') +
              '    ' +
              '[' +
              record.message.http_x_forwarded_for +
              ']'
            }}
          </div>
        </template>
      </template>

      <template #expandedRowRender="{ record }">
        <JsonViewer :value="record.message" boxed :expanded="true" />
      </template>
    </a-table>
  </div>
</template>

<script setup lang="ts">
  import 'vue3-json-viewer/dist/index.css';
  import { onMounted, reactive } from 'vue';
  import { JsonViewer } from 'vue3-json-viewer';
  import { message } from 'ant-design-vue';
  import FilterForm from './components/filter.vue';
  import { gateQuery } from '@/api/log/gateall';
  defineOptions({
    name: 'GateLogs',
  });
  const columns = [
    { title: '时间', width: 220, dataIndex: ['message', 'time_str'], fixed: true, sorter: true },
    { title: '状态码', width: 80, dataIndex: ['message', 'status'] },
    { title: '响应', width: 80, dataIndex: ['message', 'request_time'] },
    // { title: '_id', width: 120, dataIndex: '_id' },
    { title: '内容', dataIndex: 'message' },
  ];

  const state = reactive({
    historyPage: 1,
    localSearchData: {},
    tableLoading: false,
    dataSource: [],
    sizeList: ['100', '200', '300', '400', '500'], //一页能显示条数
    size: 100, //当前页显示多少条
    page: 1, //当前页
    total: 0, //总条数,在获取后台数据时将数组的length赋值给total
    timeSorter: 'descend',
    search_after: [],
    scrollType: 'no',
  });
  const handleTableChange = (pagination, filters, sorter) => {
    // console.log('sorter.column', sorter.column);
    // console.log('sorter.column.dataIndex', sorter.column.dataIndex);
    if (sorter.column.title == '时间') {
      state.scrollType = 'no';
      state.page = 1;
      state.timeSorter = sorter.order;
      getLogsList();
    }
  };
  const onChange = (page, size) => {
    console.log('change page', page);
    state.page = page;
    state.size = size;
    if (page - state.historyPage == 1) {
      // 下一页 加上search_after参数
      if (state.dataSource.length > 0) {
        state.search_after = state.dataSource.slice(-1)[0].search_after;
        state.scrollType = 'next';
      }

      getLogsList();
    } else if (page - state.historyPage == -1) {
      // 上一页 加上search_after参数
      if (state.dataSource.length > 0) {
        state.search_after = state.dataSource[0].search_after;
        state.scrollType = 'prev';
      }
      getLogsList();
    } else if (page > 99 && Math.abs(page - state.historyPage) > 1) {
      message.error('超过99页的请一页一页翻,将使用search_after搜索，最后一页请时间倒序即可');
      state.page = state.historyPage;
    } else {
      state.scrollType = 'no';
      getLogsList();
    }
  };
  const getLogsList = () => {
    const requestData = Object.assign({}, state.localSearchData, {
      timeSorter: state.timeSorter,
      page: state.page,
      size: state.size,
    });
    if (state.scrollType != 'no') {
      requestData.search_after = state.search_after;
      requestData.scrollType = state.scrollType;
    }

    state.tableLoading = true;
    state.dataSource = [];
    gateQuery(requestData).then((res) => {
      state.dataSource = res?.data;
      state.tableLoading = false;
      state.total = res?.count;
      state.historyPage = res?.historyPage;
    });
  };

  const searchClick = (searchData) => {
    state.localSearchData = searchData;
    state.total = 0;
    state.scrollType = 'no';
    state.page = 1;
    getLogsList();
  };
  onMounted(() => {});
</script>

<style lang="less" scoped>
  .screen {
    background: white;
    :deep(.ant-table-thead > tr > th) {
      font-weight: bold;
    }
    :deep(.ant-table-tbody > tr > td) {
      font-size: 12px;
      // color: white !important;
      // background: black;
    }
  }
</style>
