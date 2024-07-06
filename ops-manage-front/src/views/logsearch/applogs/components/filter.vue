<template>
  <div class="div1">
    <div class="div1-form1">
      <a-form ref="formRef" :model="formState" layout="inline">
        <a-form-item name="component">
          <a-select
            v-model:value="formState.component"
            style="width: 150px"
            allow-clear
            placeholder="请选择组件"
            show-search
            :dropdown-match-select-width="false"
            @change="componentChange"
          >
            <a-select-option
              v-for="item in state.componentList"
              :key="item.id"
              :value="item.datasource_id + '|' + item.component"
            >
              {{ item.component }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item name="app">
          <a-select
            v-model:value="formState.app"
            style="width: 220px"
            allow-clear
            placeholder="请选择应用"
            show-search
            :dropdown-match-select-width="false"
            @change="appChange"
          >
            <a-select-option v-for="item in state.appList" :key="item.app" :value="item.app">
              {{ item.app }}
            </a-select-option>
          </a-select>
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
          <a-button type="primary" @click="handleOpenProper">更多</a-button>
        </a-form-item>
      </a-form>
      <a-drawer
        v-model:visible="properOpen"
        :root-style="{ color: 'blue' }"
        title="更多条件"
        placement="right"
      >
        <div style="min-width: 350px; max-width: 500px; overflow-y: scroll">
          <a-form
            ref="popFormRef"
            :model="formState"
            :label-col="{ span: 6 }"
            :wrapper-col="{ span: 18 }"
          >
            <a-form-item label="日志路径" name="log_path">
              <a-input
                v-model:value="formState.log_path"
                allow-clear
                placeholder="请输入log_path"
              />
            </a-form-item>
            <a-form-item label="traceId" name="traceId">
              <a-input v-model:value="formState.traceId" allow-clear placeholder="请输入traceId" />
            </a-form-item>
            <a-form-item label="className" name="className">
              <a-input
                v-model:value="formState.className"
                allow-clear
                placeholder="请输入className"
              />
            </a-form-item>
            <a-form-item label="是否过滤uri" name="filterflag">
              <a-switch v-model:checked="formState.filterflag" @change="filterFlagChange" />
            </a-form-item>
            <a-form-item v-if="formState.filterflag" label="过滤日志内容" name="allignore">
              <a-textarea
                v-model:value="formState.allignore"
                placeholder="|#|分割，例如：school-auth|#|school-account"
              />
            </a-form-item>
          </a-form>
          <a-button @click="resetPopForm()">重置</a-button>
          &nbsp;
          <a-button @click="closeProper">关闭</a-button>
        </div></a-drawer
      >
    </div>
    <div class="div1-form2">
      <a-form :model="formState" layout="inline">
        <a-form-item name="msg">
          <a-input
            v-model:value="formState.msg"
            style="min-width: 300px; max-width: 450px"
            allow-clear
            placeholder="请输入msg"
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
        <a-form-item name="level">
          <a-checkbox-group v-model:value="formState.level">
            <a-checkbox value="CRITICAL" name="type">CRITICAL</a-checkbox>
            <a-checkbox value="ERROR" name="type">ERROR</a-checkbox>
            <a-checkbox value="WARN" name="type">WARN</a-checkbox>
            <a-checkbox value="INFO" name="type">INFO</a-checkbox>
            <a-checkbox value="DEBUG" name="type">DEBUG</a-checkbox>
          </a-checkbox-group>
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
  import { getAppfilter, getAppList } from '@/api/log/app';
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
    log_path: '',
    queryType: 'phase',
    component: undefined,
    app: undefined,
    searchTime: [undefined, undefined],
    msg: '',
    traceId: '',
    level: [],
    className: '',
    filterflag: false,
    allignore: '',
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
    if (formState.app && formState.component) {
      emit('searchClick', Object.fromEntries(Object.entries(formState)));
    } else {
      message.error('请先选择应用组件');
    }
  };
  const filterFlagChange = async () => {
    console.log(' filterFlagChange()>>>');
    formState.allignore = '';
    if (formState.filterflag && formState.app && formState.component) {
      await getAppfilter({ app: formState.app, component: formState.component }).then((res) => {
        if (res?.data) {
          formState.allignore = res?.data.join('|#|');
        }
      });
    }
  };
  const appChange = () => {
    filterFlagChange();
  };
  const componentChange = () => {
    console.log(formState.component);
    state.appList = [];
    getAppList({ component: formState.component }).then((res) => (state.appList = res.data));
    filterFlagChange();
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

  const initData = async () => {
    const end = new Date();
    const start = new Date();
    const urlQuery = route.query;
    console.log('urlQuery>>>', urlQuery);
    let startTime = urlQuery?.startTime;
    let endTime = urlQuery?.endTime;
    if (urlQuery.component) {
      formState.component = urlQuery.component;
    }
    if (urlQuery.app) {
      formState.app = urlQuery.app;
    }
    if (urlQuery.level) {
      formState.level = urlQuery.level.split(',');
    }
    if (urlQuery.msg) {
      formState.msg = urlQuery.msg;
    }
    if (urlQuery.traceId) {
      formState.traceId = urlQuery.traceId;
    }
    if (urlQuery.log_path) {
      formState.log_path = urlQuery.log_path;
    }
    if (urlQuery.className) {
      formState.className = urlQuery.className;
    }
    if (urlQuery.filterflag) {
      formState.filterflag = urlQuery.filterflag;
      if (formState.filterflag == true) {
        formState.filterflag = true;
        await filterFlagChange();
      }
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
      start.setTime(start.getTime() - 30 * 60 * 1000);
      formState.searchTime = [formatDateTime(start), formatDateTime(end)];
      // formState.searchTime = [moment().subtract(1, 'h'), moment()];
    }
    if (formState.app) {
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
