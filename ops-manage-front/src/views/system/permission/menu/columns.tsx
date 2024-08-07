import { Tag } from 'ant-design-vue';
import type { TableColumn } from '@/components/core/dynamic-table';
// import { Avatar, Space, Tag } from 'ant-design-vue';

export type TableListItem = API.MenuListResultItem;
export type TableColumnItem = TableColumn<TableListItem>;

/**
 * 将对应菜单类型转为字符串字意
 */
const getMenuType = (type) => {
  switch (type) {
    case 0:
      return '目录';
    case 1:
      return '菜单';
    case 2:
      return '权限';
    default:
      return '';
  }
};

export const baseColumns: TableColumnItem[] = [
  {
    title: '名称',
    dataIndex: 'name',
    width: 240,
  },
  {
    title: '图标',
    width: 80,
    dataIndex: 'icon',
    align: 'center',
    customRender: ({ record }) => record.icon && <icon-font type={record.icon} size="22" />,
  },
  {
    title: '类型',
    width: 80,
    align: 'center',
    dataIndex: 'type',
    customRender: ({ record }) => getMenuType(record.type),
  },
  {
    title: '节点路由',
    dataIndex: 'router',
    align: 'center',
    width: 240,
  },
  {
    title: '路由缓存',
    dataIndex: 'keepalive',
    align: 'center',
    width: 80,
    customRender: ({ record }) => record.type === 1 && (record.keepalive ? '是' : '否'),
  },
  {
    title: '路由显示',
    dataIndex: 'isShow',
    align: 'center',
    width: 80,
    customRender: ({ record }) => record.type !== 2 && (record.isShow ? '是' : '否'),
  },
  {
    title: '文件路径',
    width: 280,
    align: 'center',
    dataIndex: 'viewPath',
  },
  {
    title: '权限',
    width: 300,
    align: 'center',
    dataIndex: 'perms',
    customRender: ({ record }) =>
      record.type == 2 && (
        <div>
          {record.perms?.split(',').map((i) => (
            <Tag color="blue" key={i}>
              {i}
            </Tag>
          ))}
        </div>
      ),
  },
  {
    title: '排序号',
    width: 80,
    align: 'center',
    dataIndex: 'orderNum',
  },
  {
    title: '更新时间',
    width: 180,
    align: 'center',
    dataIndex: 'updatedAt',
  },
];
