import { Space, Tag } from 'ant-design-vue';
import type { TableColumn } from '@/components/core/dynamic-table';

export type TableListItem = API.UserListPageResultItem;
export type TableColumnItem = TableColumn<TableListItem>;
const statusValueEnum = {
  1: '启动',
  0: '禁用',
};
export const baseColumns: TableColumnItem[] = [
  // {
  //   title: '头像',
  //   width: 80,
  //   dataIndex: 'head_img',
  //   hideInSearch: true,
  //   customRender: ({ record }) => <Avatar src={record.headImg} />,
  // },
  {
    title: '编号',
    width: 60,
    dataIndex: 'id',
    align: 'center',
  },
  {
    title: '中文名',
    width: 80,
    dataIndex: 'realname',
    align: 'center',
  },
  {
    title: '用户名',
    width: 80,
    align: 'center',
    dataIndex: 'name',
  },
  {
    title: '所在部门',
    dataIndex: 'departmentName',
    hideInSearch: true,
    align: 'center',
    width: 100,
  },
  {
    title: '所属角色',
    dataIndex: 'roleNames',
    align: 'center',
    hideInSearch: true,
    width: 200,
    customRender: ({ record }) => (
      <Space>
        {record.roleNames.map((item) => (
          <Tag color={'success'} key={item}>
            {item}
          </Tag>
        ))}
      </Space>
    ),
  },

  // {
  //   title: '邮箱',
  //   width: 120,
  //   align: 'center',
  //   dataIndex: 'email',
  // },
  // {
  //   title: '手机',
  //   width: 120,
  //   align: 'center',
  //   dataIndex: 'phone',
  // },
  // {
  //   title: '备注',
  //   width: 120,
  //   align: 'center',
  //   dataIndex: 'remark',
  // },
  {
    title: '状态',
    dataIndex: 'status',
    width: 60,
    hideInSearch: true,
    filters: Object.keys(statusValueEnum).map((val: any) => {
      return { text: statusValueEnum[val], value: val };
    }),
    formItemProps: {
      component: 'Select',
      componentProps: {
        options: [
          {
            label: '启用',
            value: 1,
          },
          {
            label: '禁用',
            value: 0,
          },
        ],
      },
    },
    customRender: ({ record }) => {
      const isEnable = record.status === 1;
      return <Tag color={isEnable ? 'success' : 'red'}>{isEnable ? '启用' : '禁用'}</Tag>;
    },
  },
];
