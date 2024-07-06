export const powerDict = {
  list: 'alarm/identity/list',
  add: 'alarm/identity/add',
  update: 'alarm/identity/update',
  delete: 'alarm/identity/delete',
  info: 'alarm/identity_info',
  alarm_query: 'alarm/alarm_query',
  alarm_hisgram: 'alarm/alarm_hisgram',
  alarm_locate: 'alarm/alarm_locate',
  alarmsimilar: 'alarm/alarmsimilar',
  alarmexist: 'alarm/alarmexist',
  api: 'alarm/identity',
} as const;

// export const values = Object.values(powerDict);

// export type SysRolePerms = typeof values[number];

export default powerDict;
