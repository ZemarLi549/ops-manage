export const powerDict = {
  list: 'log/gatepass/list',
  add: 'log/gatepass/add',
  update: 'log/gatepass/update',
  delete: 'log/gatepass/delete',
  info: 'log/gatepass/info',
  api: 'log/gatepass',
} as const;

// export const values = Object.values(powerDict);

// export type SysRolePerms = typeof values[number];

export default powerDict;
