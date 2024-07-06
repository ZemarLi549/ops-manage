<template>
  <div class="screen">
    <a-row :gutter="4">
      <FilterForm @searchClick="searchClick" />
    </a-row>
    <a-spin :spinning="state.hisgramLoading">
      <div style="width: 100%; height: 250px">
        <HisGramBar :show-data="hisgramBarData" />
      </div>
    </a-spin>
    <div style="width: 100%; padding: 10px 0; white-space: nowrap; overflow-x: scroll">
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
      </a-pagination>
    </div>
    <!-- <img v-for="(item, key) in LEVEL_PIC" :key="key" :src="item" /> -->

    <a-table
      row-key="_id"
      size="default"
      :columns="columns"
      :data-source="state.dataSource"
      :scroll="{ x: 1000 }"
      :loading="state.tableLoading"
      :pagination="false"
      @change="handleTableChange"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.dataIndex === 'message'">
          <div style="max-height: 50px; overflow-y: scroll">
            {{ record.message.message }}
          </div>
        </template>
        <template v-else-if="column.dataIndex === 'action'">
          <span>
            <a class="a-class" @click="normalLocate(record)">定位</a>
            <br />
            <a class="a-class" @click="filterLocate(record)">过滤定位</a>
          </span>
        </template>
      </template>

      <template #expandedRowRender="{ record }">
        <JsonViewer :value="record.message" boxed :expanded="true" />
      </template>
    </a-table>
    <div ref="mod">
      <a-modal
        v-model:visible="state.locateModalShow"
        style="width: 90%; top: 10px"
        :title="null"
        :footer="null"
        :get-container="() => $refs.mod"
        :mask-closable="false"
      >
        <CommonList
          v-if="state.locateModalShow"
          :local-search-data="state.localSearchData"
          :record="state.record"
          :locate-type="locateType"
        />
      </a-modal>
    </div>
  </div>
</template>

<script setup lang="ts">
  import 'vue3-json-viewer/dist/index.css';
  import { onMounted, reactive, ref } from 'vue';
  import { JsonViewer } from 'vue3-json-viewer';
  import { message } from 'ant-design-vue';
  import CommonList from './components/logDialog.vue';
  import FilterForm from './components/filter.vue';
  import HisGramBar from './components/hisgram-bar.vue';
  import { appQuery, appHisGram } from '@/api/log/app';
  defineOptions({
    name: 'AppLogs',
  });
  //请求是否完成
  // const LEVEL_PIC = {
  //   disaster: 'https://pic.imgdb.cn/item/65570357c458853aef6eff10.jpg',
  //   normal: 'https://pic.imgdb.cn/item/65570357c458853aef6eff2c.jpg',
  //   recovery: 'https://pic.imgdb.cn/item/65570357c458853aef6eff42.jpg',
  //   serious: 'https://pic.imgdb.cn/item/65570357c458853aef6eff6b.jpg',
  //   urgent: 'https://pic.imgdb.cn/item/65570357c458853aef6eff84.jpg',
  // };
  const locateType = ref('normal');
  const columns = [
    { title: '时间', width: 220, dataIndex: ['message', 'time_str'], sorter: true },
    // { title: '_id', width: 120, dataIndex: '_id' },
    { title: '内容', dataIndex: 'message' },
    {
      title: '操作',
      dataIndex: 'action',
      width: 100,
      fixed: true,
    },
  ];
  const hisgramBarData = reactive({
    dataList: [],
  });
  const state = reactive({
    record: {},
    locateModalShow: false,
    showHisGram: false,
    hisgramLoading: false,
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
  const getAppHisGram = () => {
    const requestData = Object.assign({}, state.localSearchData, {
      timeSorter: state.timeSorter,
      page: 1,
      size: 0,
    });
    state.hisgramLoading = true;
    hisgramBarData.dataList = [];
    appHisGram(requestData).then((res) => {
      hisgramBarData.dataList = res?.data;
      state.hisgramLoading = false;
    });
  };
  const normalLocate = (record) => {
    locateType.value = 'normal';
    state.record = record;
    state.locateModalShow = true;
  };
  const filterLocate = (record) => {
    locateType.value = 'filter';
    state.record = record;
    state.locateModalShow = true;
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
    appQuery(requestData).then((res) => {
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
    getAppHisGram();
  };
  onMounted(() => {});
</script>

<style lang="less" scoped>
  .screen {
    background: white;

    /deep/ .ant-modal-close svg {
      color: white;
    }

    .a-class {
      color: #1890ff;
    }
    /deep/ .ant-modal-body {
      padding: 0px !important; /* 将背景设置为透明 */
    }
    // /deep/ .t-header {
    //   height: 36px;
    // }
    // /deep/ .t-header h4 {
    //   font-size: 0px !important;
    // }
    // /deep/ .t-header ul.t-shell-dots li {
    //   width: 0px !important;
    //   height: 0px !important;
    // }
    /deep/.ant-table-thead > tr > th {
      font-weight: bold;
    }
    /deep/ .ant-table-tbody > tr > td {
      font-size: 12px;
      // white-space: pre-wrap !important;
      // color: white !important;
      // background: black;
    }
  }
</style>
