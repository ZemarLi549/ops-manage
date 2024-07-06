<template>
  <div class="div1">
    <div class="div1-form1">
      <a-form ref="formRef" :model="formState" layout="inline">
        <a-form-item name="msg">
          <a-input
            v-model:value="formState.msg"
            style="min-width: 300px; max-width: 450px"
            allow-clear
            placeholder="查询descripiton"
          >
            <template #addonBefore>
              <a-select
                v-model:value="formState.queryType"
                style="min-width: 50px; max-width: 80px"
              >
                <a-select-option value="phase">短语</a-select-option>
                <a-select-option value="segmen">分词</a-select-option>
              </a-select>
            </template>
          </a-input>
        </a-form-item>
        <a-form-item name="searchTime">
          <a-range-picker
            v-model:value="formState.searchTime"
            max-width="500"
            show-time
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            :ranges="dateRange()"
            :placeholder="['开始时间', '结束时间']"
          />
        </a-form-item>

        <a-form-item>
          <a-button type="primary" @click="searchStartFunc">搜索</a-button>
        </a-form-item>

        <a-form-item>
          <a-popover title="更多条件" :visible="properOpen" trigger="click" placement="bottomRight">
            <template #content>
              <div style="min-width: 350px; max-width: 600px; overflow-y: scroll">
                <a-form
                  ref="popFormRef"
                  :model="formState"
                  :label-col="{ span: 6 }"
                  :wrapper-col="{ span: 18 }"
                >
                  <a-form-item label="状态" name="status">
                    <a-select v-model:value="formState.status" allow-clear>
                      <a-select-option value="firing">告警触发</a-select-option>
                      <a-select-option value="resolved">告警恢复</a-select-option>
                    </a-select>
                  </a-form-item>
                  <a-form-item label="告警类型" name="execution">
                    <a-select v-model:value="formState.execution" allow-clear mode="multiple">
                      <a-select-option value="一般告警">一般告警</a-select-option>
                      <a-select-option value="发送告警">发送告警</a-select-option>
                      <a-select-option value="折叠告警">折叠告警</a-select-option>
                      <a-select-option value="必须告警">必须告警</a-select-option>
                      <a-select-option value="忽略告警">忽略告警</a-select-option>
                    </a-select>
                  </a-form-item>
                  <a-form-item label="告警标签" name="labels">
                    <a-input
                      v-model:value="formState.labels"
                      allow-clear
                      placeholder="例如group=节点监控"
                    />
                  </a-form-item>
                  <a-form-item label="主题" name="alarm_summary">
                    <a-input
                      v-model:value="formState.alarm_summary"
                      allow-clear
                      placeholder="请输入alarm_summary"
                    />
                  </a-form-item>
                  <a-form-item label="告警等级" name="severity">
                    <a-select v-model:value="formState.severity" allow-clear mode="multiple">
                      <a-select-option value="一般">一般</a-select-option>
                      <a-select-option value="警告">警告</a-select-option>
                      <a-select-option value="严重">严重</a-select-option>
                      <a-select-option value="紧急">紧急</a-select-option>
                      <a-select-option value="灾难">灾难</a-select-option>
                    </a-select>
                  </a-form-item>
                  <a-form-item label="告警名称" name="alertname">
                    <a-input
                      v-model:value="formState.alertname"
                      allow-clear
                      placeholder="请输入alertname"
                    />
                  </a-form-item>
                  <a-form-item label="指纹ID" name="alarm_id">
                    <a-input-number
                      v-model:value="formState.alarm_id"
                      style="width: 200px"
                      allow-clear
                      placeholder="请输入指纹id,alarm_id"
                    />
                  </a-form-item>
                  <a-form-item label="告警ID" name="srmid">
                    <a-input-number
                      v-model:value="formState.srmid"
                      style="width: 200px"
                      allow-clear
                      placeholder="请输入告警方式id,srmid"
                    />
                  </a-form-item>
                  <a-form-item label="告警实例" name="instance">
                    <a-input
                      v-model:value="formState.instance"
                      allow-clear
                      placeholder="请输入instance"
                    />
                  </a-form-item>
                  <a-form-item label="告警分组" name="group">
                    <a-input
                      v-model:value="formState.group"
                      allow-clear
                      placeholder="请输入group"
                    />
                  </a-form-item>
                  <a-form-item label="告警源" name="source">
                    <a-input
                      v-model:value="formState.source"
                      allow-clear
                      placeholder="请输入source"
                    />
                  </a-form-item>
                  <a-form-item label="是否过滤" name="filterflag">
                    <a-switch v-model:checked="formState.filterflag" />
                  </a-form-item>
                  <a-form-item v-if="formState.filterflag" label="过滤desc" name="allignore">
                    <a-textarea
                      v-model:value="formState.allignore"
                      placeholder="|#|分割，例如：school-auth|#|school-account"
                    />
                  </a-form-item>
                </a-form>
                <a-button @click="resetPopForm()">重置</a-button>
                &nbsp;
                <a-button @click="closeProper">关闭</a-button>
              </div>
            </template>
            <a-button type="primary" @click="handleOpenProper">更多</a-button>
          </a-popover>
        </a-form-item>
      </a-form>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { onMounted, reactive, ref, defineEmits } from 'vue';
  import { useRoute } from 'vue-router';
  import { message } from 'ant-design-vue';
  import { dateRange } from '@/utils/picker';

  // import { getDataListByPage, createData, deleteData, updateData } from '@/api/log/apppass';
  import { getDataListByPage as getComponentDataList } from '@/api/log/component';

  const route = useRoute();
  const state = reactive({
    loading: false,
    componentList: [],
    appList: [],
  });
  const properOpen = ref<boolean>(false);
  const closeProper = () => {
    properOpen.value = false;
  };
  const handleOpenProper = () => {
    properOpen.value = true;
  };
  const formState = reactive({
    status: '',
    queryType: 'phase',
    component: undefined,
    app: undefined,
    searchTime: [undefined, undefined],
    msg: '',
    execution: [],
    labels: '',
    severity: [],
    source: '',
    group: '',
    alertname: '',
    instance: '',
    alarm_summary: '',
    filterflag: false,
    allignore: '',
    srmid: 0,
    alarm_id: 0,
  });
  const formRef = ref();
  const popFormRef = ref();
  const resetPopForm = () => {
    popFormRef.value.resetFields();
  };
  const emit = defineEmits(['searchClick']);
  const getComponentData = () => {
    getComponentDataList({ field_type: 'applog' }).then((res) => (state.componentList = res.data));
  };
  const searchStartFunc = () => {
    if (formState.searchTime) {
      emit('searchClick', Object.fromEntries(Object.entries(formState)));
    } else {
      message.error('请先选择时间范围');
    }
  };

  const formatDateTime = (date) => {
    const y = date.getFullYear();
    let m = date.getMonth() + 1;
    m = m < 10 ? `0${m}` : m;
    let d = date.getDate();
    d = d < 10 ? `0${d}` : d;
    let h = date.getHours();
    h = h < 10 ? `0${h}` : h;
    let minute = date.getMinutes();
    minute = minute < 10 ? `0${minute}` : minute;
    let second = date.getSeconds();
    second = second < 10 ? `0${second}` : second;
    return `${y}-${m}-${d} ${h}:${minute}:${second}`;
  };

  const initData = () => {
    const end = new Date();
    const start = new Date();
    const urlQuery = route.query;
    console.log('urlQuery>>>', urlQuery);
    let startTime = urlQuery?.startTime;
    let endTime = urlQuery?.endTime;
    if (urlQuery.msg) {
      formState.msg = urlQuery.msg;
    }
    if (urlQuery.execution) {
      formState.execution = urlQuery.execution;
    }
    if (urlQuery.status) {
      formState.status = urlQuery.status;
    }
    if (urlQuery.labels) {
      formState.labels = urlQuery.labels;
    }

    if (startTime || endTime) {
      console.log('query defalt >>>');
      if (startTime && startTime.indexOf('T') > 0) {
        const dateTmp = startTime.replace(/-/g, '/').replace(/T/g, '/');
        startTime = Date.parse(dateTmp);
        start.setTime(parseInt(startTime));
      }
      if (endTime && endTime.indexOf('T') > 0) {
        const dateTmp = endTime.replace(/-/g, '/').replace(/T/g, '/');
        endTime = Date.parse(dateTmp);
        end.setTime(parseInt(endTime));
      }
      formState.searchTime = [formatDateTime(start), formatDateTime(end)];
    } else {
      start.setTime(start.getTime() - 24 * 60 * 60 * 1000);
      formState.searchTime = [formatDateTime(start), formatDateTime(end)];
      // formState.searchTime = [moment().subtract(1, 'h'), moment()];
    }
    if (urlQuery.startTime) {
      searchStartFunc();
    }
  };
  onMounted(() => {
    getComponentData();
    initData();
  });
</script>

<style lang="less" scoped>
  :deep(.ant-select-selector) {
    border-radius: 10px !important;
  }
  .div1 {
    width: 100%;
    min-height: 100px;
    overflow-x: scroll;
    background: linear-gradient(to top right, rgba(229, 233, 239, 0.5), rgba(212, 219, 229, 0.6));

    margin-bottom: 10px;
    // border-radius: 20px;
  }
  .div1-form1 {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    align-items: center;
    position: relative;
    margin-top: 10px;
    margin-bottom: 10px;
  }
  .div1-form2 {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    align-items: center;
    position: relative;
  }
</style>
