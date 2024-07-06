<template>
  <SplitPanel>
    <template #left-content>
      <div class="flex justify-between">
        <div>组织架构</div>
        <Space>
          <Tooltip v-if="$auth('sys.dept.add')" placement="top">
            <template #title>新增部门 </template>
            <PlusOutlined @click="openDeptModal({})" />
          </Tooltip>
          <Tooltip placement="top">
            <template #title>刷新 </template>
            <SyncOutlined :spin="deptListLoading" @click="fetchDeptList" />
          </Tooltip>
        </Space>
      </div>
      <Tree
        v-model:expandedKeys="state.expandedKeys"
        auto-expand-parent
        :tree-data="state.deptTree"
        @select="onTreeSelect"
      >
        <template #title="{ key, title, formData }">
          <Dropdown :trigger="['contextmenu']">
            <span>{{ title }}</span>
            <template #overlay>
              <Menu>
                <Menu.Item
                  key="1"
                  :disabled="!$auth('sys.dept.update')"
                  @click="openDeptModal(formData)"
                >
                  编辑 <EditOutlined />
                </Menu.Item>
                <Menu.Item key="2" :disabled="!$auth('sys.dept.delete')" @click="delDept(key)">
                  删除 <DeleteOutlined />
                </Menu.Item>
              </Menu>
            </template>
          </Dropdown>
        </template>
      </Tree>
    </template>
    <template #right-content>
      <div style="margin: 10px 10px; width: 220px">
        <Input.Search
          v-model="userSearchParams.searchVal"
          placeholder="模糊查询"
          enter-button="搜索"
          allow-clear
          :loading="searchloading"
          @search="searchUserlist"
        />
      </div>
      <DynamicTable
        :loading="userListLoading"
        header-title="用户管理"
        title-tooltip="用户管理"
        :columns="columns"
        :row-selection="rowSelection"
        :data-source="userlistData?.data"
        @change="filterChange"
      >
        <template v-if="isCheckRows" #title>
          <Alert class="w-full" type="info" show-icon>
            <template #message>
              已选 {{ isCheckRows }} 项
              <a-button type="link" @click="rowSelection.selectedRowKeys = []">取消选择</a-button>
            </template>
          </Alert>
        </template>
        <template #toolbar>
          <a-button type="primary" :disabled="!$auth('sys.user.add')" @click="openUserModal({})">
            <PlusOutlined /> 新增
          </a-button>
          <a-button
            type="success"
            :disabled="!isCheckRows || !$auth('sys.dept.transfer')"
            @click="openTransferUserModal"
          >
            <SwapOutlined /> 转移
          </a-button>
          <a-button
            type="danger"
            :disabled="!isCheckRows || !$auth('sys.user.delete')"
            @click="delRowConfirm(rowSelection.selectedRowKeys)"
          >
            <DeleteOutlined /> 删除
          </a-button>
        </template>
      </DynamicTable>
      <div class="float-right" style="margin-right: 20px">
        <Pagination
          :total="userlistData?.count"
          :current="userSearchParams.currPage"
          :page-size="userSearchParams.pageSize"
          :page-size-options="['5', '10', '15', '20']"
          align="right"
          :show-total="(total) => `共 ${total} 条数据`"
          show-size-changer
          show-quick-jumper
          @change="handlePagination"
        />
      </div>
    </template>
  </SplitPanel>
</template>

<script setup lang="tsx">
  import { ref, reactive, computed, onMounted } from 'vue';
  import {
    SyncOutlined,
    PlusOutlined,
    EditOutlined,
    DeleteOutlined,
    ExclamationCircleOutlined,
    SwapOutlined,
  } from '@ant-design/icons-vue';
  import {
    Tree,
    Dropdown,
    Space,
    Tooltip,
    Modal,
    Alert,
    Menu,
    Pagination,
    Input,
  } from 'ant-design-vue';
  import { userSchemas, deptSchemas, updatePswSchemas, transferUserSchemas } from './formSchemas';
  import { baseColumns, type TableListItem, type TableColumnItem } from './columns';
  import type { TreeDataItem } from '@/core/permission/utils';
  import { SplitPanel } from '@/components/basic/split-panel';
  import { useTable } from '@/components/core/dynamic-table';
  import {
    deleteUsers,
    getUserListPage,
    getUserInfo,
    createUser,
    updateUser,
    updateUserPassword,
  } from '@/api/system/user';
  import { createDept, deleteDept, updateDept, getDeptList, transferDept } from '@/api/system/dept';
  import { useFormModal } from '@/hooks/useModal/index';
  import { formatDept2Tree, findChildById } from '@/core/permission/utils';

  defineOptions({
    name: 'SystemUser',
  });

  interface State {
    expandedKeys: number[];
    departmentIds: number[];
    deptTree: TreeDataItem[];
  }

  const [DynamicTable, dynamicTableInstance] = useTable({ pagination: false, search: false });
  const [showModal] = useFormModal();

  const deptListLoading = ref(false);
  const userListLoading = ref(false);
  const searchloading = ref(false);

  const state = reactive<State>({
    expandedKeys: [],
    departmentIds: [],
    deptTree: [],
  });

  const userSearchParams = reactive<any>({
    currPage: 1,
    pageSize: '5',
    status: '',
    searchVal: '',
    deptIds: '',
  });
  const userlistData = reactive<any>({
    data: [],
    count: 0,
  });
  const handlePagination = async (page, size) => {
    console.log('page>>>', page);
    userSearchParams.currPage = page;
    userSearchParams.pageSize = size;
    await fetchUserList();
  };
  const searchUserlist = (searchText: any) => {
    userSearchParams.searchVal = searchText;

    fetchUserList();
  };
  const filterChange = (page: any, filters: any) => {
    if (filters?.status) {
      userSearchParams.status = filters?.status.join(',');
    }
    fetchUserList();
  };

  const rowSelection = ref({
    selectedRowKeys: [] as number[],
    onChange: (selectedRowKeys: number[], selectedRows: TableListItem[]) => {
      console.log(`selectedRowKeys: ${selectedRowKeys}`, 'selectedRows: ', selectedRows);
      rowSelection.value.selectedRowKeys = selectedRowKeys;
    },
  });

  // 是否勾选了表格行
  const isCheckRows = computed(() => rowSelection.value.selectedRowKeys.length);

  /**
   * @description 打开部门弹窗
   */
  const openDeptModal = async (record: Partial<API.SysDeptListResult> = {}) => {
    console.log('record', record);

    const [formRef] = await showModal<any>({
      modalProps: {
        title: `${record.id ? '编辑' : '新增'}部门`,
        width: 700,
        onFinish: async (values) => {
          console.log('新增/编辑部门', values);
          values.id = record.id;
          await (record.id ? updateDept : createDept)(values);
          fetchDeptList();
        },
      },
      formProps: {
        labelWidth: 100,
        schemas: deptSchemas,
      },
    });

    formRef?.updateSchema([
      {
        field: 'parentId',
        componentProps: {
          treeDefaultExpandedKeys: [-1].concat(record?.keyPath || []),
          treeData: [
            {
              value: -1,
              title: '#',
              children: state.deptTree,
            },
          ],
        },
      },
    ]);

    formRef?.setFieldsValue({
      ...record,
      parentId: record.parentId ?? -1,
    });
  };

  /**
   * @description 将选中的用户转移至某部门
   */
  const openTransferUserModal = async () => {
    const [formRef] = await showModal({
      modalProps: {
        title: '转移部门',
        width: 700,
        onFinish: async (values) => {
          await transferDept({
            departmentId: values.departmentId,
            userIds: rowSelection.value.selectedRowKeys.map((n) => n),
          });
        },
      },
      formProps: {
        labelWidth: 100,
        schemas: transferUserSchemas,
      },
    });

    formRef?.updateSchema([
      {
        field: 'departmentId',
        componentProps: { treeData: state.deptTree },
      },
    ]);
  };

  /**
   * @description 打开用户弹窗
   */
  const openUserModal = async (record: Partial<TableListItem> = {}) => {
    const [formRef] = await showModal<any>({
      modalProps: {
        title: `${record.id ? '编辑' : '新增'}用户`,
        width: 700,
        onFinish: async (values) => {
          console.log('新增/编辑用户', values);
          values.id = record.id;
          await (record.id ? updateUser : createUser)(values);
          dynamicTableInstance?.reload();
        },
      },
      formProps: {
        labelWidth: 100,
        schemas: userSchemas,
      },
    });

    formRef?.updateSchema([
      {
        field: 'departmentId',
        componentProps: {
          treeDefaultExpandedKeys:
            findChildById(record?.departmentId, state.deptTree)?.keyPath || [],
          treeData: state.deptTree,
        },
      },
    ]);

    formRef?.setFieldsValue(record);
    if (record?.id) {
      const { roles } = await getUserInfo({ userId: record.id });
      formRef?.setFieldsValue({ roles });
    }
  };

  /**
   * 打开更新用户密码弹窗
   */
  const openUpdatePasswordModal = async (record: TableListItem) => {
    await showModal({
      modalProps: {
        title: `修改密码(${record.name})`,
        width: 700,
        onFinish: async (values) => {
          await updateUserPassword({
            id: record.id,
            password: values.password,
          });
        },
      },
      formProps: {
        labelWidth: 100,
        schemas: updatePswSchemas,
      },
    });
  };

  const delDept = (departmentId: number) => {
    Modal.confirm({
      title: '确定要删除该部门吗?',
      icon: <ExclamationCircleOutlined />,
      centered: true,
      onOk: async () => {
        await deleteDept({ id: departmentId });
        fetchDeptList();
      },
    });
  };

  /**
   * 获取部门列表
   */
  const fetchDeptList = async () => {
    deptListLoading.value = true;
    const dept = await getDeptList().finally(() => (deptListLoading.value = false));
    state.deptTree = formatDept2Tree(dept);
    state.expandedKeys = [...state.expandedKeys, ...state.deptTree.map((n) => Number(n.key))];
  };

  const fetchUserList = async () => {
    userListLoading.value = true;
    const params = Object.assign({}, userSearchParams, {
      departmentIds: state.departmentIds.length ? state.departmentIds : undefined,
    });
    params.page = userSearchParams.currPage;
    params.size = userSearchParams.pageSize;
    delete params.currPage;
    delete params.pageSize;
    await getUserListPage(params).then((res) => {
      userListLoading.value = false;
      console.log(res);
      userlistData.data = res?.data;
      userlistData.count = res?.count;
    });
  };

  /**
   * @description 表格删除行
   */
  const delRowConfirm = async (userId: number | number[]) => {
    if (Array.isArray(userId)) {
      Modal.confirm({
        title: '确定要删除所选的用户吗?',
        icon: <ExclamationCircleOutlined />,
        centered: true,
        onOk: async () => {
          await deleteUsers({ userIds: userId });
          fetchUserList();
        },
      });
    } else {
      await deleteUsers({ userIds: [userId] });
      fetchUserList();
    }
  };

  /**
   * 点击部门
   */
  const onTreeSelect = (selectedKeys: number[]) => {
    state.departmentIds = selectedKeys;
    console.log(state.departmentIds);
    userSearchParams.deptIds = state.departmentIds.join(',');
    fetchUserList();
  };

  // const loadTableData = async (params: LoadDataParams) => {
  //   const data = await getUserListPage({
  //     ...params,
  //     departmentIds: state.departmentIds.length ? state.departmentIds : undefined,
  //   });
  //   rowSelection.value.selectedRowKeys = [];
  //   return data;
  // };

  const columns: TableColumnItem[] = [
    ...baseColumns,
    {
      title: '操作',
      width: 150,
      dataIndex: 'ACTION',
      align: 'center',
      fixed: 'right',
      actions: ({ record }) => [
        {
          label: '编辑',
          auth: {
            perm: 'sys.user.update',
            effect: 'disable',
          },
          onClick: () => openUserModal(record),
        },
        {
          label: '改密',
          auth: 'sys.user.password',
          onClick: () => openUpdatePasswordModal(record),
        },
        {
          label: '删除',
          auth: 'sys.user.delete',
          popConfirm: {
            title: '你确定要删除吗？',
            onConfirm: () => delRowConfirm(record.id),
          },
        },
      ],
    },
  ];

  onMounted(() => {
    fetchDeptList();
    fetchUserList();
  });
</script>

<style></style>
