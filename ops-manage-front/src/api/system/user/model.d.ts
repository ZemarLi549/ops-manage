declare namespace API {
  type UserListPageResultItem = {
    createdAt: string;
    departmentId: number;
    email: string;
    headImg: string;
    id: number;
    name: string;
    phone: string;
    remark: string;
    status: number;

    updatedAt: string;
    realname: string;
    departmentName: string;
    roleNames: string[];
    keyPath?: number[];
  };

  /** 获取用户列表结果 */
  type UserListPageResult = UserListPageResultItem[];

  /** 创建用户参数 */
  type CreateUserParams = {
    departmentId: number;
    name: string;
    realname: string;
    roles: number[];
    email: string;
    phone: string;
    remark: string;
    status: number;
    deptPower: number;
  };

  /** 管理员用户详情 */
  type AdminUserInfo = {
    createAt: string;
    updateAt: string;
    id: number;
    departmentId: number;
    name: string;
    realname: string;
    password: string;
    psalt: string;
    headImg: string;
    email: string;
    phone: string;
    remark: string;
    status: number;
    roles: string[];
    departmentName: string;
  };

  /** 更新管理员用户参数 */
  type UpdateAdminInfoParams = {
    departmentId: number;
    name: string;
    realname: string;
    roles: number[];
    email: string;
    phone: string;
    remark: string;
    status: number;
    id: number;
  };

  /** 更新管理员密码 */
  type UpdateAdminUserPassword = {
    id: number;
    password: string;
  };
}
