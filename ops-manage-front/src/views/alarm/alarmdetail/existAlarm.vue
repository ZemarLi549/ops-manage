<template>
  <div>
    <div style="margin-bottom: 16px">
      <div style="margin: 10px 10px; width: 220px">
        <a-select
          v-model:value="state.labels"
          style="width: 150px"
          allow-clear
          placeholder="请选择label"
          mode="multiple"
          :dropdown-match-select-width="false"
          @change="componentChange"
        >
          <a-select-option v-for="(item, key) in props.identityKv" :key="key" :value="key">
            {{ key }}
          </a-select-option>
        </a-select>
      </div>
      <a-table
        :row-selection="rowSelection"
        :columns="columns"
        :loading="state.loading"
        :data-source="state.data"
        :pagination="false"
        :scroll="{ x: 300 }"
        row-key="id"
        :locale="{ emptyText: '暂无数据' }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'id'">
            <a class="a-class" @click="jumpRefresh(record.id)">{{ record.id }}</a>
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
  import { inject, onMounted, reactive, ref } from 'vue';
  import { useRouter } from 'vue-router';
  import { alarmExistData } from '@/api/alarm/identity';
  const router = useRouter();
  const typeColor = {
    0: { text: '消除', color: 'gray', value: 0 },
    1: { text: '正在处理', color: 'pink', value: 1 },
    2: { text: '处理完成', color: 'green', value: 2 },
    3: { text: '暂时忽略', color: 'cyan', value: 3 },
    4: { text: '未处理', color: 'orange', value: 4 },
    5: { text: '自动恢复', color: 'blue', value: 5 },
  };
  defineOptions({
    name: 'AlarmExists',
  });
  const jumpRefresh = (alarmid) => {
    router.push({ name: 'alarmdetail', query: { alarmid } }).then(() => {
      router.go(0); // 强制刷新
    });
  };
  const props = defineProps({
    // 传进来的数据
    identityKv: {
      type: Object,
      default() {
        return {};
      },
    },
    identityId: {
      type: Number,
      default() {
        return 1;
      },
    },
  });
  const componentChange = () => {
    getDataList();
  };
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
    },
    {
      title: '指纹',
      dataIndex: 'identity_tag_kv',
    },
    {
      title: '次数',
      dataIndex: 'times',
    },
    {
      title: '状态',
      dataIndex: 'status',
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
    searchloading: false,
    sourceDataList: [],
    labels: ['job'],
  });

  const message = inject('$message');
  // 获取信息
  const getDataList = async () => {
    const params = {
      page: state.page,
      size: state.size,
      identityId: props.identityId,
      labels: state.labels.join(','),
      identityKv: props.identityKv,
    };
    state.loading = true;
    await alarmExistData(params).then(
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

  onMounted(() => {
    getDataList();
  });
</script>

<style>
  .a-class {
    color: #1890ff;
  }
</style>
