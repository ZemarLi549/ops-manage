export const powerDict = {
  list: 'alarm/user/list',
  add: 'alarm/user/add',
  update: 'alarm/user/update',
  delete: 'alarm/user/delete',
  info: 'alarm/user/info',
  api: 'alarm/user',
} as const;

// export const values = Object.values(powerDict);

// export type SysRolePerms = typeof values[number];

export default powerDict;
