export const sysRole = {
  list: 'sys/role/list',
  add: 'sys/role/add',
  update: 'sys/role/update',
  delete: 'sys/role/delete',
  info: 'sys/role/info',
  api: 'sys/role',
} as const;

export const values = Object.values(sysRole);

export type SysRolePerms = typeof values[number];

export default sysRole;
