<template>
  <div>
    <a-row :gutter="4" class="rowStyle" type="flex" justify="space-around" align="middle">
      <a-col :span="24" class="colStyle">
        <Title>指纹标签</Title>
        <a-descriptions size="small" title="" bordered>
          <a-descriptions-item v-for="(val, key) in props.record.identity_tag_kv" :label="key">{{
            val
          }}</a-descriptions-item>
        </a-descriptions>
      </a-col>
    </a-row>
    <a-row :gutter="4" class="rowStyle" type="flex" justify="space-around" align="middle">
      <a-col :span="24" class="colStyle">
        <div class="block-box">
          <Title>修改状态</Title>
          <a-form
            ref="formRef"
            :model="formState"
            :rules="rules"
            :label-col="{ span: 4 }"
            :wrapper-col="{ span: 18 }"
          >
            <a-form-item label="处理状态" name="status">
              <a-select v-model:value="formState.status">
                <a-select-option
                  v-for="typeItem in Object.values(typeColor)"
                  :key="typeItem.value"
                  :value="typeItem.value"
                >
                  {{ typeItem.text }}
                </a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item v-if="formState.status == 3" label="忽略截至时间" name="ignore_to">
              <a-date-picker
                v-model:value="formState.ignore_to"
                show-time
                type="date"
                placeholder="Select Time"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
              />
            </a-form-item>
            <a-form-item v-if="formState.status == 3" label="记录忽略" name="record_ignore">
              <a-switch v-model:checked="formState.record_ignore" />
            </a-form-item>
            <a-form-item label="处理人员" name="handler">
              <a-input v-model:value="formState.handler" allow-clear placeholder="请输入姓名" />
            </a-form-item>
            <a-form-item>
              <a-button style="width: 30%; margin-left: 40%" type="primary" @click="onStatusSubmit"
                >确定</a-button
              >
            </a-form-item>
          </a-form>
        </div>
      </a-col>
    </a-row>
    <a-row :gutter="4" class="rowStyle" type="flex" justify="space-around" align="middle">
      <a-col :span="24" class="colStyle">
        <Title>告警记录</Title>
        <a-table
          row-key="_id"
          size="default"
          :columns="columns"
          :data-source="state.dataSource"
          :scroll="{ x: 200 }"
          :loading="state.tableLoading"
          :pagination="false"
          @change="handleTableChange"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.dataIndex === 'message'">
              <div style="max-height: 250px; overflow-y: hidden">
                <span>{{ '[' + record.message.startsAt + ']' }}</span>
                <span style="font-weight: bold">{{
                  '【' + record.message.alarm_summary + '】'
                }}</span
                ><span>{{ record.message.alarm_desc }}</span>
              </div>
            </template>
          </template>

          <template #expandedRowRender="{ record }">
            <JsonViewer :value="record.message" boxed :expanded="true" />
          </template>
        </a-table>
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
      </a-col>
    </a-row>
    <a-row :gutter="4" class="rowStyle" type="flex" justify="space-around" align="middle">
      <a-col :span="24" class="colStyle">
        <Title>告警评论</Title>
        <CommentData :key="state.commentDataKey" :identity-id="props.record.id" />
      </a-col>
    </a-row>
    <a-row :gutter="4" class="rowStyle" type="flex" justify="space-around" align="middle">
      <a-col :span="24" class="colStyle">
        <a-spin :spinning="state.solutionLoading">
          <div class="block-box">
            <Title>告警总结</Title>
            <a-form
              ref="solutionFormRef"
              :model="solutionFormState"
              :rules="rules"
              :label-col="{ span: 4 }"
              :wrapper-col="{ span: 18 }"
            >
              <a-form-item label="影响范围" name="reach">
                <a-textarea
                  v-model:value="solutionFormState.reach"
                  placeholder="请输入告警影响范围"
                  :rows="2"
                />
              </a-form-item>
              <a-form-item label="告警原因" name="reason">
                <a-textarea
                  v-model:value="solutionFormState.reason"
                  placeholder="请输入告警告警原因"
                  :rows="2"
                />
              </a-form-item>
              <a-form-item label="解决方案" name="solution">
                <a-textarea
                  v-model:value="solutionFormState.solution"
                  placeholder="请输入告警解决方案"
                  :rows="2"
                />
              </a-form-item>
              <a-form-item label="更新人" name="updated_by">
                <a-input
                  v-model:value="solutionFormState.updated_by"
                  :disabled="true"
                  placeholder="更新人"
                />
              </a-form-item>

              <a-form-item>
                <a-button
                  style="width: 30%; margin-left: 40%"
                  type="primary"
                  @click="onSolutionSubmit"
                  >确定</a-button
                >
              </a-form-item>
            </a-form>
          </div>
        </a-spin>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
  import { inject, onMounted, reactive, ref } from 'vue';
  import 'vue3-json-viewer/dist/index.css';
  import { JsonViewer } from 'vue3-json-viewer';
  import CommentData from './comment.vue';
  import Title from '@/components/cardtitle/Title.vue';
  import { postData, alarmQueryData } from '@/api/alarm/identity';
  import {
    getDataListByPage as solutionDataList,
    createData as createSolutionData,
  } from '@/api/alarm/solution';
  // defineOptions({
  //   name: 'AlarmIdentityDeploy',
  // });
  const props = defineProps({
    // 传进来的数据
    record: {
      type: Object,
      default() {
        return {};
      },
    },
  });
  const alarmTypeColor = {
    wechat: 'cyan',
    phone: 'orange',
    sms: 'pink',
    email: 'green',
    ding: 'blue',
  };

  const columns = [
    // { title: '时间', width: 220, dataIndex: ['message', 'startsAt'], sorter: true },
    // { title: '_id', width: 120, dataIndex: '_id' },
    { title: '内容', dataIndex: 'message', sorter: true },
    {
      title: '状态',
      dataIndex: ['message', 'status'],
      filterMultiple: false,
      filters: [
        { text: 'firing', value: 'firing' },
        { text: 'resolved', value: 'resolved' },
      ],
    },
    {
      title: '类型',
      dataIndex: ['message', 'execution'],
      filters: [
        { text: '发送告警', value: '发送告警' },
        { text: '折叠告警', value: '折叠告警' },
        { text: '必须告警', value: '必须告警' },
        { text: '忽略告警', value: '忽略告警' },
      ],
    },
  ];
  const handleTableChange = (pagination, filters, sorter) => {
    // console.log('sorter.column', sorter.column);
    // console.log('sorter.column.dataIndex', sorter.column.dataIndex);
    state.page = 1;
    state.scrollType = 'no';
    if (sorter.column) {
      if (sorter.column.title == '内容') {
        state.timeSorter = sorter.order;
      } else {
        state.timeSorter = 'descend';
      }
    }

    // console.log('filters>>>', filters);
    if (filters['message.execution']) {
      state.execution = filters['message.execution'].join(',');
    } else {
      state.execution = '';
    }
    if (filters['message.status']) {
      state.alarm_status = filters['message.status'].join(',');
    } else {
      state.alarm_status = '';
    }

    getLogsList();
  };
  const onStatusSubmit = () => {
    formRef.value.validate().then(() => {
      const params = Object.fromEntries(Object.entries(formState));
      if (params.status !== 3) {
        params.ignore_to = null;
        params.record_ignore = 1;
      }
      params.opType = 'modifyStatus';
      params.id = props.record.id;
      // postData(params);
      postData(params).finally(() => {
        state.commentDataKey += 1;
      });
    });
  };
  const typeColor = {
    0: { text: '消除', color: 'gray', value: 0 },
    1: { text: '正在处理', color: 'pink', value: 1 },
    2: { text: '处理完成', color: 'green', value: 2 },
    3: { text: '暂时忽略', color: 'cyan', value: 3 },
    4: { text: '未处理', color: 'orange', value: 4 },
    5: { text: '自动恢复', color: 'blue', value: 5 },
  };

  const state = reactive({
    loading: false,
    data: [],
    size: 5,
    page: 1,
    total: 0,
    solutionLoading: false,
    dataSource: [],
    historyPage: 1,
    timeSorter: 'descend',
    execution: [],
    alarm_status: [],
    search_after: [],
    scrollType: 'no',
    localSearchData: {},
    commentDataKey: 0,
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
  });

  const formRef = ref();
  const formState = reactive({
    handler: '',
    status: 1,
    ignore_to: null,
    record_ignore: true,
  });
  const solutionFormRef = ref();
  const solutionFormState = reactive({
    reach: '',
    reason: '',
    solution: '',
    updated_by: '',
  });
  const rules = {};

  const resetForm = () => {
    formRef.value.resetFields();
  };
  const message = inject('$message');

  // 获取信息

  // 翻页
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
    } else if (page * size > 9999 && Math.abs(page - state.historyPage) > 1) {
      message.error(
        `超过${Math.floor(
          9999 / size,
        )}页的请一页一页翻,将使用search_after搜索，最后一页请时间倒序即可`,
      );
      state.page = state.historyPage;
      state.page = state.historyPage;
    } else {
      state.scrollType = 'no';
      getLogsList();
    }
  };
  const getLogsList = () => {
    const requestData = Object.assign({}, state.localSearchData, {
      timeSorter: state.timeSorter,
      status: state.alarm_status,
      execution: state.execution,
      page: state.page,
      size: state.size,
      // fromTime: props.record?.created_at,
    });
    if (state.scrollType != 'no') {
      requestData.search_after = state.search_after;
      requestData.scrollType = state.scrollType;
    }

    state.tableLoading = true;
    state.dataSource = [];
    alarmQueryData(requestData).then((res) => {
      state.dataSource = res?.data;
      state.tableLoading = false;
      state.total = res?.count;
      state.historyPage = res?.historyPage;
    });
  };

  const initData = () => {
    Object.assign(formState, props.record);
    formState.record_ignore = formState.record_ignore === 1 ? true : false;
    state.localSearchData = { alarm_id: props.record.id };
    getSolutionDataList();
    getLogsList();
  };
  const onSolutionSubmit = () => {
    const params = Object.fromEntries(Object.entries(solutionFormState));
    params.identity_id = props.record.id;
    createSolutionData(params).then((res) => {
      if (res.code && res.code == 200) {
        getSolutionDataList();
      }
    });
  };
  // 获取信息
  const getSolutionDataList = async () => {
    const params = {
      identity_id: props.record.id,
    };
    state.solutionLoading = true;
    await solutionDataList(params).then((res) => {
      state.solutionLoading = false;
      const resData = res.data;
      console.log(resData);
      solutionFormState.reason = resData.reason;
      solutionFormState.reach = resData.reach;
      solutionFormState.solution = resData.solution;
      solutionFormState.updated_by = resData.updated_by;
    });

    // state.size = data.size
  };
  onMounted(() => {
    initData();
  });
</script>

<style lang="less" scoped>
  .colStyle {
    border-radius: 4px;
    box-shadow: 0px 1px 2px rgba(0, 0, 0, 0.3);
    transition: transform 0.3s ease-in-out;
    padding: 4px;
  }
  .rowStyle {
    margin-bottom: 8px;
  }
  .block-box {
    width: 100%;
    padding: 1px;
    color: black;
    z-index: 10;
    border-bottom: 1px solid rgba(255, 255, 255, 0.4);
    border-left: 1px solid rgba(255, 255, 255, 0.4);
    background: linear-gradient(to top right, rgba(229, 233, 239, 0.5), rgba(212, 219, 229, 0.6));
    box-shadow: 1px;
    backdrop-filter: blur(6px); /*  元素后面区域添加模糊效果 */
    border-radius: 4px;
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
