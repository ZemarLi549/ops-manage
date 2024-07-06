<template>
  <div>
    <div style="margin-bottom: 16px">
      <a-collapse v-model:activeKey="activeKey">
        <a-collapse-panel key="1" header="说明">
          <p>告警指纹规则配置，关联告警方式id,就会达到收敛功能！</p>
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
          <template v-else-if="column.dataIndex === 'configIds'">
            <a-tag v-for="configId in record.configIds" :key="configId" color="green">
              {{ configId }}
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
          <a-form-item label="规则ID" name="id">
            <a-input v-model:value="formState.id" allow-clear placeholder="请输入id" />
          </a-form-item>
          <a-form-item label="规则名称" name="name">
            <a-input v-model:value="formState.name" allow-clear placeholder="请输入username" />
          </a-form-item>
          <a-form-item label="关键字" name="rule_keys">
            <a-input
              v-model:value="formState.rule_keys"
              allow-clear
              placeholder="例如：id,type,instance"
            />
          </a-form-item>
          <a-form-item label="正则提取" name="rule_re">
            <a-input
              v-model:value="formState.rule_re"
              allow-clear
              placeholder="例如 level&&.*level\:(.*?)!|#|project&&.*project\:(.*?)!就会新生成project,level关键字"
            />
          </a-form-item>
          <a-form-item label="评分" name="rate">
            <a-input-number
              v-model:value="formState.rate"
              style="width: 200px"
              allow-clear
              placeholder="请输入评分，默认1"
            />
          </a-form-item>
          <a-form-item label="告警间隔" name="freq">
            <a-input-number
              v-model:value="formState.freq_num"
              allow-clear
              placeholder="告警间隔,0就是不收敛"
            >
              <template #addonAfter>
                <a-select v-model:value="formState.freq_unit" style="width: 100px">
                  <a-select-option value="minutes">minutes</a-select-option>
                  <a-select-option value="hours">hours</a-select-option>
                  <a-select-option value="days">days</a-select-option>
                  <a-select-option value="infinity">无限收敛</a-select-option>
                </a-select>
              </template>
            </a-input-number>
          </a-form-item>
          <a-form-item label="恢复间隔" name="resovle_freq">
            <a-input-number
              v-model:value="formState.resovle_freq_num"
              allow-clear
              placeholder="恢复告警间隔,0就是不收敛"
            >
              <template #addonAfter>
                <a-select v-model:value="formState.resovle_freq_unit" style="width: 100px">
                  <a-select-option value="minutes">minutes</a-select-option>
                  <a-select-option value="hours">hours</a-select-option>
                  <a-select-option value="days">days</a-select-option>
                  <a-select-option value="infinity">无限收敛</a-select-option>
                </a-select>
              </template>
            </a-input-number>
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
        <!-- <div class="itxst">
          <div>
            <draggable
              :list="state.list"
              ghost-class="ghost"
              chosen-class="chosenClass"
              animation="300"
            >
              <template #item="{ element }">
                <div class="item">
                  {{ element.name }}
                </div>
              </template>
            </draggable>
          </div>
          <div>{{ state.list }}</div>
        </div> -->
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { inject, onMounted, reactive, ref } from 'vue';

  // import draggable from 'vuedraggable';

  import { getDataListByPage, createData, deleteData, updateData } from '@/api/alarm/rule';
  defineOptions({
    name: 'AlarmRule',
  });
  const activeKey = ref(['1']);
  const labelCol = {
    span: 4,
  };
  const wrapperCol = {
    span: 20,
  };
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
    },
    {
      title: '规则名称',
      dataIndex: 'name',
    },
    {
      title: '关键字',
      dataIndex: 'rule_keys',
    },
    {
      title: '正则提取',
      dataIndex: 'rule_re',
    },

    {
      title: '评分',
      dataIndex: 'rate',
    },
    {
      title: '告警间隔',
      dataIndex: 'freq',
    },
    {
      title: '恢复间隔',
      dataIndex: 'resovle_freq',
    },
    {
      title: '告警IDs',
      dataIndex: 'configIds',
    },
    {
      title: '操作',
      dataIndex: 'action',
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
    searchloading: false,
    sourceDataList: [],
    // list: [
    //   { name: 'www.itxst.com', id: 0 },
    //   { name: 'www.baidu.com', id: 1 },
    //   { name: 'www.google.com', id: 2 },
    // ],
  });

  const addNewData = () => {
    // formState.rate = undefined;
    state.credModalStatus = 'add';
    state.credModalVisible = true;
  };

  const formRef = ref();
  const formState = reactive({
    id: 0,
    name: '',
    rule_re: '',
    rule_keys: '',
    rate: '',
    freq_num: '',
    freq_unit: 'minutes',
    resovle_freq_num: '',
    resovle_freq_unit: 'minutes',
  });
  const rules = {
    name: [
      {
        required: true,
        message: '请输入name',
        trigger: 'blur',
      },
      { pattern: /(^\S)((.)*\S)?(\S*$)/, message: '前后不能有空格' },
    ],
  };

  const onSubmit = () => {
    formRef.value.validate().then(() => {
      const params = Object.fromEntries(Object.entries(formState));
      if (params?.freq_num && params?.freq_unit) {
        params.freq = `${params?.freq_num},${params?.freq_unit}`;
        delete params.freq_num;
        delete params.freq_unit;
      }
      if (params?.resovle_freq_num && params?.resovle_freq_unit) {
        params.resovle_freq = `${params?.resovle_freq_num},${params?.resovle_freq_unit}`;
        delete params.resovle_freq_num;
        delete params.resovle_freq_unit;
      }
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
    if (record?.freq) {
      const freqList = record?.freq.split(',');
      record.freq_num = freqList[0];
      record.freq_unit = freqList[1];
      delete record.freq;
    }
    if (record?.resovle_freq) {
      const freqList = record?.resovle_freq.split(',');
      record.resovle_freq_num = freqList[0];
      record.resovle_freq_unit = freqList[1];
      delete record.resovle_freq;
    }
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
