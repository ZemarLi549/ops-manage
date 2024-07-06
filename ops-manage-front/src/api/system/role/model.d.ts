declare namespace API {
  /** 新增角色 */
  type CreateRoleParams = {
    name: string;
    remark: string;
    menus: Key[];
    depts: number[];
  };
  /** 更新角色 */
  type UpdateRoleParams = CreateRoleParams & {
    id: number;
  };

  /** 角色列表项 */
  type RoleListResultItem = {
    createdAt: string;
    updatedAt: string;
    id: number;
    name: string;
    remark: string;
  };

  /** 角色列表 */
  type RoleListResult = RoleListResultItem[];

  /** 角色详情 */
  type RoleInfoResult = {
    roleInfo: {
      createAt: string;
      updateAt: string;
      id: number;
      name: string;
      remark: string;
    };
    menus: {
      createAt: string;
      updateAt: string;
      id: number;
      roleId: number;
      menuId: number;
    }[];
    depts: {
      createAt: string;
      updateAt: string;
      id: number;
      roleId: number;
      departmentId: number;
    }[];
  };
}
