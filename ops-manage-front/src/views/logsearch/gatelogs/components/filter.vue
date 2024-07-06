<template>
  <div class="div1">
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
      <a-form-item name="domain">
        <a-select
          v-model:value="formState.domain"
          style="width: 220px"
          allow-clear
          placeholder="请选择域名"
          show-search
          :dropdown-match-select-width="false"
          @change="domainChange"
        >
          <a-select-option v-for="item in state.domainList" :key="item.domain" :value="item.domain">
            {{ item.domain }}
          </a-select-option>
        </a-select>
      </a-form-item>
      <a-form-item name="searchTime">
        <a-range-picker
          v-model:value="formState.searchTime"
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
      <div style="min-width: 350px; max-width: 500px; overflow-y: auto">
        <a-form
          ref="popFormRef"
          :model="formState"
          :label-col="{ span: 6 }"
          :wrapper-col="{ span: 18 }"
        >
          <a-form-item label="请求uri" name="uri">
            <a-input v-model:value="formState.uri" allow-clear placeholder="请输入uri" />
          </a-form-item>
          <a-form-item label="请求参数" name="args">
            <a-input v-model:value="formState.args" allow-clear placeholder="请输入args" />
          </a-form-item>
          <a-form-item label="请求端IP" name="client_ip">
            <a-input
              v-model:value="formState.client_ip"
              allow-clear
              placeholder="请输入http_x_forwarded_for"
            />
          </a-form-item>
          <a-form-item label="状态码" name="status">
            <a-checkbox-group v-model:value="formState.status">
              <a-checkbox value="101" name="type">101</a-checkbox>
              <a-checkbox value="200" name="type">200</a-checkbox>
              <a-checkbox value="301" name="type">301</a-checkbox>
              <a-checkbox value="302" name="type">302</a-checkbox>
              <a-checkbox value="400" name="type">400</a-checkbox>
              <a-checkbox value="401" name="type">401</a-checkbox>
              <a-checkbox value="403" name="type">403</a-checkbox>
              <a-checkbox value="404" name="type">404</a-checkbox>
              <a-checkbox value="499" name="type">499</a-checkbox>
              <a-checkbox value="500" name="type">500</a-checkbox>
              <a-checkbox value="501" name="type">501</a-checkbox>
              <a-checkbox value="502" name="type">502</a-checkbox>
              <a-checkbox value="503" name="type">503</a-checkbox>
              <a-checkbox value="504" name="type">504</a-checkbox>
            </a-checkbox-group>
          </a-form-item>
          <a-form-item label="请求方法" name="request_method">
            <a-checkbox-group v-model:value="formState.request_method">
              <a-checkbox value="GET" name="type">GET</a-checkbox>
              <a-checkbox value="POST" name="type">POST</a-checkbox>
              <a-checkbox value="PUT" name="type">PUT</a-checkbox>
              <a-checkbox value="DELETE" name="type">DELETE</a-checkbox>
              <a-checkbox value="OPTIONS" name="type">OPTIONS</a-checkbox>
              <a-checkbox value="HEAD" name="type">HEAD</a-checkbox>
              <a-checkbox value="TRACE" name="type">TRACE</a-checkbox>
              <a-checkbox value="CONNECT" name="type">CONNECT</a-checkbox>
            </a-checkbox-group>
          </a-form-item>
          <a-form-item label="请求总时间" name="request_time">
            <a-input
              v-model:value="formState.request_time"
              allow-clear
              placeholder=">5或>1 and <=2或<3"
            />
          </a-form-item>
          <a-form-item label="是否过滤uri" name="filterflag">
            <a-switch v-model:checked="formState.filterflag" @change="filterFlagChange" />
          </a-form-item>
          <a-form-item v-if="formState.filterflag" label="过滤uri内容" name="allignore">
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
    </a-drawer>
  </div>
</template>

<script setup lang="ts">
  import { onMounted, reactive, ref, defineEmits } from 'vue';
  import { useRoute } from 'vue-router';
  import { message } from 'ant-design-vue';
  import { dateRange } from '@/utils/picker';
  import { getGatefilter, getGateList } from '@/api/log/gate';
  // import { getDataListByPage, createData, deleteData, updateData } from '@/api/log/apppass';
  import { getDataListByPage as getComponentDataList } from '@/api/log/component';
  const route = useRoute();
  const state = reactive({
    loading: false,
    componentList: [],
    domainList: [],
  });
  const properOpen = ref<boolean>(false);
  const formState = reactive({
    args: '',
    component: undefined,
    domain: undefined,
    searchTime: [undefined, undefined],
    uri: '',
    client_ip: '',
    status: [],
    request_method: [],
    request_time: '',
    filterflag: false,
    allignore: '',
  });
  const formRef = ref();
  const popFormRef = ref();
  const resetPopForm = () => {
    popFormRef.value.resetFields();
  };
  const closeProper = () => {
    properOpen.value = false;
  };
  const handleOpenProper = () => {
    properOpen.value = true;
  };
  const emit = defineEmits(['searchClick']);
  const getComponentData = () => {
    getComponentDataList({ field_type: 'nginxlog' }).then(
      (res) => (state.componentList = res.data),
    );
  };
  const searchStartFunc = () => {
    if (formState.domain && formState.component) {
      emit('searchClick', Object.fromEntries(Object.entries(formState)));
    } else {
      message.error('请先选择域名组件');
    }
  };
  const filterFlagChange = async () => {
    console.log(' filterFlagChange()>>>');
    formState.allignore = '';
    if (formState.filterflag && formState.domain && formState.component) {
      await getGatefilter({ domain: formState.domain, component: formState.component }).then(
        (res) => {
          if (res?.data) {
            formState.allignore = res?.data.join('|#|');
          }
        },
      );
    }
  };
  const domainChange = () => {
    filterFlagChange();
  };
  const componentChange = () => {
    console.log(formState.component);
    state.domainList = [];
    getGateList({ component: formState.component }).then((res) => (state.domainList = res.data));
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
    if (urlQuery.domain) {
      formState.domain = urlQuery.domain;
    }
    if (urlQuery.status) {
      formState.status = urlQuery.status.split(',');
    }
    if (urlQuery.request_methods) {
      formState.request_methods = urlQuery.request_methods.split(',');
    }
    if (urlQuery.request_time) {
      console.log('urlQuery.request_time', urlQuery.request_time);
      formState.request_time = urlQuery.request_time;
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
    if (urlQuery.domain) {
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
    overflow-x: scroll;
    width: 100%;
    min-height: 80px;
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
    background: linear-gradient(to top right, rgba(229, 233, 239, 0.5), rgba(212, 219, 229, 0.6));

    margin-bottom: 10px;
    // border-radius: 20px;
  }
</style>
