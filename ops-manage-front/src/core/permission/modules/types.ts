import type { SysPermissionType } from './sys';

export type PermissionType = ReplaceAll<SysPermissionType, '/', '.'>;
