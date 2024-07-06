export const powerDict = {
  list: 'alarm/config/list',
  add: 'alarm/config/add',
  update: 'alarm/config/update',
  delete: 'alarm/config/delete',
  info: 'alarm/config/info',
  api: 'alarm/config',
} as const;

// export const values = Object.values(powerDict);

// export type SysRolePerms = typeof values[number];

export default powerDict;
