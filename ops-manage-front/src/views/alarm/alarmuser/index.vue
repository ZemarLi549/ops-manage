<template>
  <div>
    <div style="margin-bottom: 16px">
      <a-collapse v-model:activeKey="activeKey">
        <a-collapse-panel key="1" header="说明">
          <p>告警联系人配置！</p>
        </a-collapse-panel>
      </a-collapse>
    </div>
    <div style="margin-bottom: 16px">
      <a-space>
        <!-- <a-button v-if="$auth('log.apppass.add')" type="primary" @click="addNewData">新增</a-button> -->
        <a-button type="primary" @click="addNewData">新增</a-button>
        <a-button
          type="primary"
          danger
          :disabled="state.selectedRows.length <= 0"
          @click="removeData()"
          >批量删除</a-button
        >
      </a-space>
      <div style="margin: 10px 10px; width: 220px">
        <a-input-search
          v-model="state.searchVal"
          placeholder="模糊查询"
          enter-button="搜索"
          allow-clear
          :loading="state.searchloading"
          @search="searchDatalist"
        />
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
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'action'">
            <span>
              <a class="a-class" @click="rowEdit(record)">编辑</a>
            </span>
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
        style="width: 40%; min-width: 360px"
        :title="state.credModalStatus === 'add' ? '添加' : '编辑'"
        cancel-text="取消"
        ok-text="确定"
        :keyboard="false"
        :mask-closable="false"
        @ok="onSubmit"
        @cancel="resetForm"
      >
        <a-form
          ref="formRef"
          :model="formState"
          :rules="rules"
          :label-col="labelCol"
          :wrapper-col="wrapperCol"
        >
          <a-form-item label="用户名" name="username">
            <a-input v-model:value="formState.username" allow-clear placeholder="请输入username" />
          </a-form-item>
          <a-form-item label="中文名" name="name">
            <a-input v-model:value="formState.name" allow-clear placeholder="请输入name" />
          </a-form-item>
          <a-form-item label="手机号" name="phone">
            <a-input v-model:value="formState.phone" allow-clear placeholder="请输入手机号" />
          </a-form-item>
          <a-form-item label="邮箱" name="email">
            <a-input
              v-model:value="formState.email"
              allow-clear
              placeholder="请输入邮箱，默认<username>@iflytek.com"
            />
          </a-form-item>
          <a-form-item label="备注" name="desc">
            <a-input v-model:value="formState.desc" allow-clear placeholder="备注" />
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
  import { inject, onMounted, reactive, ref } from 'vue';

  import { getDataListByPage, createData, deleteData, updateData } from '@/api/alarm/user';
  defineOptions({
    name: 'AlarmUser',
  });
  const activeKey = ref(['1']);
  const columns = [
    {
      title: '用户名',
      dataIndex: 'username',
    },
    {
      title: '中文名',
      dataIndex: 'name',
    },
    {
      title: '手机号',
      dataIndex: 'phone',
    },

    {
      title: '邮箱',
      dataIndex: 'email',
    },
    {
      title: '备注',
      dataIndex: 'desc',
    },
    {
      title: '操作',
      dataIndex: 'action',
      // fixed: 'right',
    },
  ];
  const labelCol = {
    span: 4,
  };
  const wrapperCol = {
    span: 20,
  };
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
  });

  const addNewData = () => {
    // formState.email = undefined;
    state.credModalStatus = 'add';
    state.credModalVisible = true;
  };

  const formRef = ref();
  const formState = reactive({
    username: '',
    phone: '',
    name: '',
    email: '',
    desc: '',
  });
  const rules = {
    phone: [
      {
        pattern: /^1[3|4|5|7|8][0-9]\d{8}$/,
        message: '请输入正确的手机号',
        trigger: 'blur',
        required: true,
      },
    ],
    username: [
      {
        required: true,
        message: '请输入username',
        trigger: 'blur',
      },
      { pattern: /(^\S)((.)*\S)?(\S*$)/, message: '前后不能有空格' },
    ],
    email: [{ pattern: /(^\S)((.)*\S)?(\S*$)/, message: '前后不能有空格' }],
  };

  const onSubmit = () => {
    formRef.value.validate().then(() => {
      const params = Object.fromEntries(Object.entries(formState));
      if (state.credModalStatus == 'add') {
        params.operate = 'add';
        if (params?.id) {
          delete params.id;
        }
        createData(params).finally(() => {
          state.credModalVisible = false;
          resetForm();
          getDataList();
        });
      } else {
        updateData(params).finally(() => {
          state.credModalVisible = false;
          resetForm();
          getDataList();
        });
      }
    });
  };

  const resetForm = () => {
    formRef.value.resetFields();
  };
  const message = inject('$message');
  // 获取信息
  const getDataList = async () => {
    const params = {
      page: state.page,
      size: state.size,
      searchVal: state.searchVal,
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
  // 显示条数
  const onShowSizeChange = async (current, size) => {
    state.size = size;
    state.page = 1;
    await getDataList();
  };

  const rowSelection = {
    onChange: (selectedRowKeys, selectedRows) => {
      state.selectedRows = selectedRows;
      state.selectedRowKeys = selectedRowKeys;
    },
  };
  //模糊查询
  const searchDatalist = async (searchText) => {
    state.searchVal = searchText;
    state.searchloading = true;
    await getDataList();
    state.searchloading = false;
  };
  // 批量删除
  const removeData = async () => {
    const deleteIds = [];
    for (let i = 0; i < state.selectedRowKeys.length; i++) {
      deleteIds.push(state.selectedRowKeys[i]);
    }
    await deleteData({ deleteIds }).finally(() => {
      state.selectedRows = [];
      getDataList();
    });
  };

  // 查看详情
  const rowEdit = (record) => {
    Object.assign(formState, record);
    state.credModalStatus = 'update';
    state.credModalVisible = true;
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
