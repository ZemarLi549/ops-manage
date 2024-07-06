export const sysUser = {
  add: 'sys/user/add',
  list: 'sys/user/list',
  info: 'sys/user/info',
  update: 'sys/user/update',
  delete: 'sys/user/delete',
  password: 'sys/user/password',
  api: 'sys/user',
} as const;

export const values = Object.values(sysUser);

export type SysUserPerms = typeof values[number];

export default sysUser;
