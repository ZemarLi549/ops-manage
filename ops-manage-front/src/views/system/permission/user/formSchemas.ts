import type { FormSchema } from '@/components/core/schema-form/';
import { getRoleList } from '@/api/system/role';

export const deptSchemas: FormSchema<API.CreateDeptParams>[] = [
  {
    field: 'name',
    component: 'Input',
    label: '部门名称',
    rules: [{ required: true, type: 'string' }],
  },
  {
    field: 'parentId',
    component: 'TreeSelect',
    label: '上级部门',
    componentProps: {
      getPopupContainer: () => document.body,
    },
    rules: [{ required: true, type: 'number' }],
  },
  {
    field: 'orderNum',
    component: 'InputNumber',
    label: '排序号',
    defaultValue: 255,
    componentProps: {
      style: {
        width: '100%',
      },
    },
  },
];

export const userSchemas: FormSchema<API.CreateUserParams>[] = [
  {
    field: 'departmentId',
    component: 'TreeSelect',
    label: '所属部门',
    componentProps: {
      getPopupContainer: () => document.body,
    },
    rules: [{ required: false, type: 'number' }],
  },
  {
    field: 'deptPower',
    component: 'RadioGroup',
    label: '有无部门权限',
    defaultValue: 1,
    componentProps: {
      options: [
        {
          label: '有',
          value: 1,
        },
        {
          label: '无',
          value: 0,
        },
      ],
    },
  },

  {
    field: 'roles',
    component: 'Select',
    label: '所属角色',
    rules: [{ required: false, type: 'array' }],
    componentProps: {
      mode: 'multiple',
      request: async () => {
        const data = await getRoleList();
        return data.map((n) => ({ label: n.name, value: n.id }));
      },
    },
  },
  {
    field: 'name',
    component: 'Input',
    label: '用户名',
    rules: [{ required: true }],
  },
  {
    field: 'realname',
    component: 'Input',
    label: '中文名',
    colProps: {
      span: 12,
    },
    rules: [{ required: true }],
  },

  {
    field: 'email',
    component: 'Input',
    label: '邮箱',
    colProps: {
      span: 12,
    },
  },
  {
    field: 'phone',
    component: 'Input',
    label: '手机',
    colProps: {
      span: 12,
    },
  },
  {
    field: 'remark',
    component: 'InputTextArea',
    label: '备注',
  },
  {
    field: 'status',
    component: 'RadioGroup',
    label: '状态',
    defaultValue: 1,
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
];
/**
 * @description 更新用户密码
 */
export const updatePswSchemas: FormSchema[] = [
  {
    field: 'password',
    component: 'Input',
    label: '新密码',
    rules: [{ required: true, type: 'string' }],
  },
];
/**
 * @description 将用户转移部门
 */
export const transferUserSchemas: FormSchema[] = [
  {
    field: 'departmentId',
    component: 'TreeSelect',
    label: '转移至',
    rules: [{ required: true, type: 'number' }],
  },
];
