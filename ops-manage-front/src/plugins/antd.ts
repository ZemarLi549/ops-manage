import {
  Modal,
  Table,
  Menu,
  Input,
  Form,
  Card,
  Checkbox,
  Radio,
  Col,
  Row,
  Select,
  DatePicker,
  Pagination,
  Tooltip,
  Tag,
  Spin,
  Dropdown,
  Divider,
  Space,
  Switch,
  Tabs,
  Popconfirm,
  InputNumber,
  Collapse,
  Tree,
  Transfer,
  Popover,
  Descriptions,
  Drawer,
  Comment,
  Avatar,
} from 'ant-design-vue';
import type { App } from 'vue';

import { AButton } from '@/components/basic/button/index';

// import 'ant-design-vue/dist/antd.css';
import 'ant-design-vue/dist/antd.variable.min.css';
import 'dayjs/locale/zh-cn';

export function setupAntd(app: App<Element>) {
  app.component('AButton', AButton);

  app
    .use(Form)
    .use(Input)
    .use(Modal)
    .use(Table)
    .use(Menu)
    .use(Card)
    .use(Checkbox)
    .use(Radio)
    .use(Col)
    .use(Row)
    .use(Select)
    .use(Pagination)
    .use(Tooltip)
    .use(Tag)
    .use(Space)
    .use(Spin)
    .use(Dropdown)
    .use(Divider)
    .use(Switch)
    .use(Tabs)
    .use(Popconfirm)
    .use(InputNumber)
    .use(Collapse)
    .use(Popover)
    .use(Tree)
    .use(Transfer)
    .use(Descriptions)
    .use(Comment)
    .use(Avatar)
    .use(Drawer)
    .use(DatePicker);
}
