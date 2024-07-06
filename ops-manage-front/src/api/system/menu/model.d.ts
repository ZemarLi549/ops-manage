declare namespace API {
  type MenuListResultItem = {
    createAt: string;
    updatedAt: string;
    id: number;
    parentId: number;
    name: string;
    router: string;
    perms: string;
    /** 0: '目录', 1: '菜单', 2: '权限'  */
    type: number;
    icon: string;
    orderNum: number;
    viewPath: string;
    keepalive: boolean;
    isShow: boolean;
    keyPath?: number[];
  };

  /** 获取菜单列表参数 */
  type MenuListResult = MenuListResultItem[];

  /** 新增菜单参数 */
  type MenuAddParams = {
    type: number;
    parentId: number;
    name: string;
    orderNum: number;
    router: string;
    isShow: boolean;
    keepalive: boolean;
    icon: string;
    perms: string;
    viewPath: string;
  };

  /** 更新某项菜单参数 */
  type MenuUpdateParams = MenuAddParams & {
    menuId: number;
  };

  /** 获取菜单详情结果 */
  type MenuInfoResult = {
    menu: {
      createAt: string;
      updateAt: string;
      id: number;
      parentId: number;
      name: string;
      router: string;
      perms: string;
      type: number;
      icon: string;
      orderNum: number;
      viewPath: string;
      keepalive: boolean;
      isShow: boolean;
    };
    parentMenu: {
      createAt: string;
      updateAt: string;
      id: number;
      parentId: number;
      name: string;
      router: string;
      perms: string;
      type: number;
      icon: string;
      orderNum: number;
      viewPath: string;
      keepalive: boolean;
      isShow: boolean;
    };
  };
}
