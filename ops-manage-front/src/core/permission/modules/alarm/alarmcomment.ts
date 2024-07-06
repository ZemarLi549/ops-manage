export const powerDict = {
  list: 'alarm/comment/list',
  add: 'alarm/comment/add',
  update: 'alarm/comment/update',
  delete: 'alarm/comment/delete',
  info: 'alarm/comment/info',
  batch: 'alarm/batchcmt',
  putcmt: 'alarm/putcmt',
  api: 'alarm/comment',
} as const;

// export const values = Object.values(powerDict);

// export type SysRolePerms = typeof values[number];

export default powerDict;
