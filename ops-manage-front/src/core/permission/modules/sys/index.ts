import type { SysDeptPerms } from './dept';
import type { SysMenuPerms } from './menu';

import type { SysRolePerms } from './role';

import type { SysUserPerms } from './user';

export type SysPermissionType = SysDeptPerms | SysMenuPerms | SysRolePerms | SysUserPerms;
