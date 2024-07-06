<template>
  <div>
    <div style="margin-bottom: 16px">
      <a-collapse v-model:activeKey="activeKey">
        <a-collapse-panel key="1" header="说明">
          <p>当前存活指纹告警概览</p>
        </a-collapse-panel>
      </a-collapse>
    </div>
    <div style="margin-bottom: 16px">
      <a-space>
        <!-- <a-button v-if="$auth('log.apppass.add')" type="primary" @click="addNewData">新增</a-button> -->
        <!-- <a-button type="primary" @click="addNewData">新增</a-button> -->
        <a-tooltip>
          <template #title>状态改为消除，归到指纹历史，确定告警已解决恢复</template>
          <a-button
            type="danger"
            :disabled="state.selectedRows.length <= 0"
            @click="batchOpData('deactivate')"
            >批量消除</a-button
          >
        </a-tooltip>

        <a-tooltip>
          <template #title>如果告警间隔由长改短了，立马生效，可以重新收敛</template>
          <a-button
            type="primary"
            :disabled="state.selectedRows.length <= 0"
            @click="batchOpData('reagg')"
            >重新收敛</a-button
          >
        </a-tooltip>
        <a-button
          type="primary"
          :disabled="state.selectedRows.length <= 0"
          @click="openbtDeployModal"
          >批量处理</a-button
        >
        <a-button
          type="primary"
          :disabled="state.selectedRows.length <= 0"
          @click="openbtCommentModal"
          >批量评论</a-button
        >
      </a-space>
      <div style="width: 100%">
        <a-space :size="8">
          <div style="margin: 10px 10px; width: 200px">
            <a-input
              v-model:value="state.searchVal"
              placeholder="标签查询"
              allow-clear
              :loading="state.searchloading"
              @pressEnter="searchDatalist"
            />
          </div>
          <div style="margin: 10px 10px; width: 150px">
            <a-input
              v-model:value="state.searchID"
              placeholder="ID查询"
              allow-clear
              :loading="state.searchloading"
              @pressEnter="searchDatalist"
            />
          </div>
          <a-button size="small" type="primary" @click="searchDatalist"> 搜索 </a-button>
          <a-button type="dashed" :icon="h(ReloadOutlined)" @click="getDataList"></a-button>
          <a-select
            v-model:value="state.autoRefresh"
            placeholder="刷新间隔"
            @change="handleRefreshChange"
          >
            <a-select-option key="1" value="60000"> 1分钟 </a-select-option>
            <a-select-option key="2" value="120000"> 2分钟 </a-select-option>
            <a-select-option key="5" value="300000"> 5分钟 </a-select-option>
            <a-select-option key="10" value="600000"> 10分钟 </a-select-option>
            <a-select-option key="0" value="0"> 关闭 </a-select-option>
          </a-select>
        </a-space>
      </div>
      <a-table
        :row-selection="rowSelection"
        :columns="columns"
        :loading="state.loading"
        :data-source="state.data"
        :pagination="false"
        :scroll="{ x: 1000 }"
        row-key="id"
        :locale="{ emptyText: '暂无数据' }"
        @change="handleTableChange"
      >
        <template #expandedRowRender="{ record }">
          <!-- <span>{{ record.srmidInfo }}</span> -->
          <a-descriptions style="font-size: 11px" size="small" title="" :column="1">
            <a-descriptions-item label="名称">{{ record.srmidInfo.name }}</a-descriptions-item>
            <a-descriptions-item label="规则">{{ record.srmidInfo.rule_name }}</a-descriptions-item>
            <a-descriptions-item label="通知">
              <a-tag
                v-for="typeItem in record.srmidInfo.alarm_detail"
                :key="typeItem.alarm_type"
                :color="alarmTypeColor[typeItem.alarm_type]"
              >
                {{ typeItem.alarm_type + ':' + typeItem.alarm_user.join(',') }}
              </a-tag>
            </a-descriptions-item>
          </a-descriptions>
        </template>
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'action'">
            <a-tag
              color="green"
              style="cursor: pointer"
              @click="routePush('alarmdetail', { alarmid: record.id })"
              >查看</a-tag
            >
            <a-tag color="cyan" style="cursor: pointer" @click="rowEdit(record)">处理</a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'status'">
            <a-tag :color="typeColor[record.status]['color']">
              {{ typeColor[record.status]['text'] }}
            </a-tag>
          </template>
          <template v-else>
            <span>
              {{ record[column.dataIndex] }}
            </span>
          </template>
        </template>
      </a-table>

      <a-modal
        v-model:visible="state.credModalVisible"
        style="width: 70%; min-width: 360px"
        :title="state.credModalStatus === 'add' ? '添加' : '告警指纹处理'"
        :footer="null"
        :keyboard="false"
        :mask-closable="false"
      >
        <CommonList v-if="state.credModalVisible" :record="state.record" />
      </a-modal>
      <a-modal
        v-model:visible="state.btDeployModalVisible"
        style="width: 30%; min-width: 360px"
        title="批量处理"
        :footer="null"
        :keyboard="false"
        :mask-closable="false"
      >
        <a-form :model="deployFormState" :label-col="{ span: 4 }" :wrapper-col="{ span: 18 }">
          <a-form-item label="处理状态" name="status">
            <a-select v-model:value="deployFormState.status">
              <a-select-option
                v-for="typeItem in Object.values(typeColor)"
                :key="typeItem.value"
                :value="typeItem.value"
              >
                {{ typeItem.text }}
              </a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item v-if="deployFormState.status == 3" label="忽略截至时间" name="ignore_to">
            <a-date-picker
              v-model:value="deployFormState.ignore_to"
              show-time
              type="date"
              placeholder="Select Time"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DD HH:mm:ss"
            />
          </a-form-item>
          <a-form-item v-if="deployFormState.status == 3" label="记录忽略" name="record_ignore">
            <a-switch v-model:checked="deployFormState.record_ignore" />
          </a-form-item>
          <a-form-item label="处理人员" name="handler">
            <a-input v-model:value="deployFormState.handler" allow-clear placeholder="请输入姓名" />
          </a-form-item>
          <a-form-item>
            <a-button style="width: 30%; margin-left: 40%" type="primary" @click="onStatusSubmit"
              >确定</a-button
            >
          </a-form-item>
        </a-form>
      </a-modal>
      <a-modal
        v-model:visible="state.btCommentModalVisible"
        style="width: 30%; min-width: 360px"
        title="批量评论"
        :footer="null"
        :keyboard="false"
        :mask-closable="false"
      >
        <a-form :model="comentFormState" :label-col="{ span: 4 }" :wrapper-col="{ span: 18 }">
          <a-form-item label="告警评论" name="comment_text">
            <a-textarea
              v-model:value="comentFormState.comment_text"
              placeholder="输入告警评论"
              :rows="4"
            />
          </a-form-item>
          <a-form-item>
            <a-button style="width: 30%; margin-left: 40%" type="primary" @click="onCommentSubmit"
              >确定</a-button
            >
          </a-form-item>
        </a-form>
      </a-modal>
      <div
        class="float-right"
        style="width: 100%; padding: 10px 0; white-space: nowrap; overflow-x: scroll"
      >
        <a-pagination
          size="md"
          :show-total="(total) => `共 ${state.total} 条数据`"
          :current="state.page"
          :page-size-options="state.pageSizeOptions"
          :total="state.total"
          show-size-changer
          :page-size="state.size"
          show-less-items
          align="right"
          @change="onChange"
        >
          <template #buildOptionText="props">
            <span v-if="props.value !== '50'">{{ props.value }}条/页</span>
            <span v-if="props.value === '50'">全部</span>
          </template>
        </a-pagination>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { inject, onMounted, reactive, ref, h, onUnmounted } from 'vue';
  import { useRouter } from 'vue-router';
  import { ReloadOutlined } from '@ant-design/icons-vue';
  import CommonList from './deploy.vue';
  import { getDataListByPage, postData } from '@/api/alarm/identity';
  import { batchcreateData as batchCommentData } from '@/api/alarm/comment';
  defineOptions({
    name: 'AlarmIdentity',
  });
  const router = useRouter();
  const alarmTypeColor = {
    wechat: 'cyan',
    phone: 'orange',
    sms: 'pink',
    email: 'green',
    ding: 'blue',
  };
  const openbtCommentModal = () => {
    state.btCommentModalVisible = true;
  };
  const comentFormState = reactive({
    coment_text: '',
  });
  const onCommentSubmit = () => {
    const params = Object.fromEntries(Object.entries(comentFormState));
    const postIds = [];
    for (let i = 0; i < state.selectedRowKeys.length; i++) {
      postIds.push(state.selectedRowKeys[i]);
    }
    params.postIds = postIds;
    batchCommentData(params).finally(() => {
      state.selectedRows = [];
      state.btCommentModalVisible = false;
    });
  };

  const openbtDeployModal = () => {
    state.btDeployModalVisible = true;
  };
  const deployFormState = reactive({
    handler: '',
    status: 1,
    ignore_to: null,
    record_ignore: true,
  });
  const onStatusSubmit = () => {
    const params = Object.fromEntries(Object.entries(deployFormState));
    if (params.status !== 3) {
      params.ignore_to = null;
      params.record_ignore = 1;
    }
    params.opType = 'modifyStatus';
    const postIds = [];
    for (let i = 0; i < state.selectedRowKeys.length; i++) {
      postIds.push(state.selectedRowKeys[i]);
    }
    params.postIds = postIds;
    // postData(params);
    postData(params).finally(() => {
      state.selectedRows = [];
      state.btDeployModalVisible = false;
      getDataList();
    });
  };
  const routePush = (name, query) => {
    const routeData = router.resolve({ name, query });
    window.open(routeData.href, '_blank');
  };

  const typeColor = {
    // 0: { text: '消除', color: 'gray', value: 0 },
    1: { text: '正在处理', color: 'pink', value: 1 },
    2: { text: '处理完成', color: 'green', value: 2 },
    3: { text: '暂时忽略', color: 'cyan', value: 3 },
    4: { text: '未处理', color: 'orange', value: 4 },
    5: { text: '自动恢复', color: 'blue', value: 5 },
  };
  let intervalId = null;
  // 处理下拉选择变化事件
  const handleRefreshChange = () => {
    clearInterval(intervalId);
    if (state.autoRefresh === '0') {
      console.log('close timer', state.autoRefresh);
      clearInterval(intervalId); // 如果选择值为 0，关闭自动刷新
      intervalId = null;
    } else {
      console.log('recreate timer', state.autoRefresh);
      // 如果选择值不为 0 且定时器未启动，则开始自动刷新
      startAutoRefresh();
    }
  };
  // 启动自动刷新
  const startAutoRefresh = () => {
    intervalId = setInterval(() => {
      getDataList();
    }, state.autoRefresh); // 5秒钟刷新一次，可以根据需求调整时间间隔
  };

  const activeKey = ref(['1']);
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
    },
    {
      title: '指纹标签',
      dataIndex: 'identity_tag_kv',
    },

    {
      title: '告警次数',
      dataIndex: 'times',
      sorter: true,
      sortDirections: ['descend', 'ascend'],
    },
    {
      title: '恢复次数',
      dataIndex: 'recover_cnt',
      sorter: true,
      sortDirections: ['descend', 'ascend'],
    },
    {
      title: '统计评分',
      dataIndex: 'score',
      sorter: true,
      sortDirections: ['descend', 'ascend'],
    },
    {
      title: '状态',
      dataIndex: 'status',
      filters: Object.values(typeColor),
    },
    {
      title: '处理时长',
      dataIndex: 'duration_time',
      sorter: true,
      sortDirections: ['descend', 'ascend'],
    },
    {
      title: '创建',
      dataIndex: 'created_at',
      sorter: true,
      sortDirections: ['descend', 'ascend'],
    },
    {
      title: '更新',
      dataIndex: 'updated_at',
      sorter: true,
      sortDirections: ['descend', 'ascend'],
    },
    {
      title: '处理人',
      dataIndex: 'handler',
    },
    {
      title: '操作',
      dataIndex: 'action',
      width: 60,
      // fixed: 'right',
    },
  ];

  let selectedRowKeys;
  const state = reactive({
    selectedRows: [],
    selectedRowKeys,
    loading: false,
    data: [],
    size: 10,
    page: 1,
    total: 0,
    pageSizeOptions: ['5', '10', '15', '20'],
    credModalVisible: false,
    credModalStatus: 'add',
    searchVal: '',
    searchID: '',
    orderField: '',
    orderType: '',
    status: '',
    searchloading: false,
    sourceDataList: [],
    autoRefresh: '60000',
    record: {},
    btDeployModalVisible: false,
    btCommentModalVisible: false,
  });

  const message = inject('$message');
  const handleTableChange = (pagination, filters, sorter) => {
    // console.log('sorter.column', sorter.column);
    // console.log('sorter.column.dataIndex', sorter.column.dataIndex);
    state.page = 1;
    // console.log('sorter>>>', sorter);
    // console.log('filters>>>', filters);
    if (sorter.column) {
      state.orderType = sorter.order;
      if (sorter.column.title == '处理时长') {
        state.orderField = 'process_time';

        getDataList();
      } else {
        state.orderField = sorter.column.dataIndex;
      }
    }
    if (filters.status) {
      state.status = filters.status.join(',');
    } else {
      state.status = '';
    }
    getDataList();
  };
  // 获取信息
  const getDataList = async () => {
    const params = {
      page: state.page,
      size: state.size,
      searchVal: state.searchVal,
      id: state.searchID,
      orderField: state.orderField,
      orderType: state.orderType,
      status: state.status,
    };
    state.loading = true;
    await getDataListByPage(params).then(
      (res) => ((state.data = res.data), (state.total = res.count), (state.loading = false)),
    );

    // state.size = data.size
  };
  // 翻页
  const onChange = async (pageNumber, size) => {
    state.page = pageNumber;
    state.size = size;
    await getDataList();
  };

  const rowSelection = {
    onChange: (selectedRowKeys, selectedRows) => {
      state.selectedRows = selectedRows;
      state.selectedRowKeys = selectedRowKeys;
    },
  };
  //模糊查询
  const searchDatalist = async () => {
    state.searchloading = true;
    await getDataList();
    state.searchloading = false;
  };
  // 批量删除
  const batchOpData = async (opType) => {
    const postIds = [];
    for (let i = 0; i < state.selectedRowKeys.length; i++) {
      postIds.push(state.selectedRowKeys[i]);
    }
    await postData({ postIds, opType }).finally(() => {
      state.selectedRows = [];
      getDataList();
    });
  };

  // 查看详情
  const rowEdit = (record) => {
    state.record = record;
    state.credModalStatus = 'update';
    state.credModalVisible = true;
  };
  const clearTimer = () => {
    if (intervalId) {
      clearInterval(intervalId);
    }
  };
  onUnmounted(() => {
    clearTimer();
  });
  onMounted(() => {
    getDataList();
    startAutoRefresh();
  });
</script>

<style lang="less" scoped>
  .a-class {
    color: #1890ff;
  }
  :deep(.ant-table-thead > tr > th) {
    font-weight: bold;
    font-size: 12px;
  }
  :deep(.ant-table-tbody > tr > td) {
    font-size: 11px;
    // white-space: pre-wrap !important;
    // color: white !important;
    // background: black;
  }
</style>
