<template>
  <div>
    <div style="margin-bottom: 16px">
      <a-collapse v-model:activeKey="activeKey">
        <a-collapse-panel key="1" header="说明">
          <p>组件名和数据源联合唯一，一个数据源下不能出现重复的组件名！</p>
        </a-collapse-panel>
      </a-collapse>
    </div>
    <div style="margin-bottom: 16px">
      <a-space>
        <a-button v-if="$auth('log.source.add')" type="primary" @click="addNewData">新增</a-button>
        <a-button
          v-if="$auth('log.source.delete')"
          type="primary"
          danger
          :disabled="state.selectedRows.length <= 0"
          @click="removeData()"
          >批量删除</a-button
        >
      </a-space>
    </div>
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
            <a v-if="$auth('log.source.update')" class="a-class" @click="rowEdit(record)">编辑</a>
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
        <a-form-item label="日志源选择">
          <a-select v-model:value="formState.datasource_id" placeholder="请选择源">
            <a-select-option v-for="item in state.sourceDataList" :key="item.id" :value="item.id">
              {{ item.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="数据源类型">
          <a-select v-model:value="formState.source" placeholder="请选择类型">
            <a-select-option v-for="(value, key) in sourceDict" :key="key" :value="key">
              {{ value }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="组件名" name="component">
          <a-input v-model:value="formState.component" allow-clear placeholder="aops-xxx" />
        </a-form-item>

        <a-form-item label="索引正则">
          <a-input v-model:value="formState.index_str" allow-clear placeholder="index_str" />
        </a-form-item>
        <a-form-item label="时间字段">
          <a-input v-model:value="formState.time_field" allow-clear placeholder="time_field" />
        </a-form-item>
        <a-form-item label="字段类型">
          <a-input
            v-model:value="formState.field_type"
            allow-clear
            placeholder="applog,nginxlog..."
          />
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
</template>

<script>
  import { defineComponent, inject, onMounted, reactive, ref } from 'vue';
  import { getDataListByPage, createData, deleteData, updateData } from '@/api/log/component';
  import { getDataListByPage as getSourceDataList } from '@/api/log/source';
  const activeKey = ref(['1']);
  const sourceDict = {
    es: 'ES',
    sls: '阿里云SLS',
    cls: '腾讯云CLS',
  };
  const columns = [
    {
      title: '数据源id',
      dataIndex: 'datasource_id',
    },
    {
      title: '数据源类型',
      dataIndex: 'source',
    },
    {
      title: '组件名',
      dataIndex: 'component',
    },
    {
      title: '索引正则',
      dataIndex: 'index_str',
    },
    {
      title: '时间字段',
      dataIndex: 'time_field',
    },
    {
      title: '字段类型',
      dataIndex: 'field_type',
    },
    {
      title: '操作',
      dataIndex: 'action',
      fixed: 'right',
    },
  ];

  export default defineComponent({
    name: 'Manage',
    components: {},
    setup() {
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
      const getSourceData = () => {
        getSourceDataList({ isSelect: true }).then((res) => (state.sourceDataList = res.data));
      };
      const addNewData = () => {
        state.credModalStatus = 'add';
        state.credModalVisible = true;
      };

      const formRef = ref();
      const formState = reactive({
        source: 'es',
        component: '',
        index_str: '',
        time_field: '',
        field_type: '',
      });
      const rules = {
        // name: [
        //   {
        //     required: true,
        //     message: '请输入名称',
        //     trigger: 'blur',
        //   },
        //   {
        //     min: 1,
        //     max: 25,
        //     message: '名称长度应为1~25',
        //     trigger: 'blur',
        //   },
        // ],
        // username: [
        //   {
        //     required: true,
        //     message: '请输入username',
        //     trigger: 'blur',
        //   },
        // ],
      };

      const onSubmit = () => {
        formRef.value.validate().then(() => {
          const params = Object.fromEntries(Object.entries(formState));
          if (state.credModalStatus == 'add') {
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
        console.log('edit>>>', record);

        Object.assign(formState, record);
        state.credModalStatus = 'update';
        state.credModalVisible = true;
      };
      onMounted(() => {
        getDataList();
        getSourceData();
      });
      return {
        sourceDict,
        columns,
        state,

        addNewData,
        formRef,
        formState,
        rules,
        onSubmit,
        resetForm,

        labelCol: {
          span: 4,
        },
        wrapperCol: {
          span: 19,
        },

        onShowSizeChange,
        onChange,
        rowSelection,
        removeData,
        rowEdit,
        searchDatalist,
        activeKey,
      };
    },
  });
</script>

<style>
  .a-class {
    color: #1890ff;
  }
</style>
