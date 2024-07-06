<template>
  <div>
    <div style="margin-bottom: 16px">
      <a-collapse v-model:activeKey="activeKey">
        <a-collapse-panel key="1" header="说明">
          <p
            >告警id配置，关联规则，就会收敛，告警类型有(折叠告警，发送告警，忽略告警，必须告警)！否则就是一般告警,复制只要打开编辑,id改成新的就自动复制了</p
          >
        </a-collapse-panel>
      </a-collapse>
    </div>
    <div style="margin-bottom: 16px">
      <a-space>
        <!-- <a-button v-if="$auth('log.apppass.add')" type="primary" @click="addNewData">新增</a-button> -->
        <a-button type="primary" @click="addNewData">新增</a-button>
        <a-button
          type="primary"
          danger
          :disabled="state.selectedRows.length <= 0"
          @click="removeData()"
          >批量删除</a-button
        >
      </a-space>
      <div>
        <a-space :size="8">
          <div style="margin: 10px 10px; width: 200px">
            <a-input
              v-model:value="state.searchVal"
              placeholder="模糊查询"
              allow-clear
              :loading="state.searchloading"
              @pressEnter="searchDatalist"
            />
          </div>
          <div style="margin: 10px 10px; width: 100px">
            <a-input
              v-model:value="state.searchID"
              placeholder="ID查询"
              allow-clear
              :loading="state.searchloading"
              @pressEnter="searchDatalist"
            />
          </div>
          <!-- <div style="margin: 10px 10px; width: 220px"> -->
          <a-button size="small" type="primary" @click="searchDatalist"> 搜索 </a-button>
          <!-- </div> -->
        </a-space>
      </div>
      <a-table
        :row-selection="rowSelection"
        :columns="columns"
        :loading="state.loading"
        :data-source="state.data"
        :pagination="false"
        :scroll="{ x: 1000 }"
        row-key="id"
        :locale="{ emptyText: '暂无数据' }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'action'">
            <span>
              <a class="a-class" @click="rowEdit(record)">编辑</a>
            </span>
          </template>
          <template v-else-if="column.dataIndex === 'alarm_detail'">
            <a-tag
              v-for="typeItem in record.alarm_detail"
              :key="typeItem.alarm_type"
              :color="typeColor[typeItem.alarm_type]"
            >
              {{ typeItem.alarm_type + ':' + typeItem.alarm_user.join(',') }}
            </a-tag>
          </template>
          <template v-else>
            <span>
              {{ record[column.dataIndex] }}
            </span>
          </template>
        </template>
        <template #expandedRowRender="{ record }">
          <JsonViewer :value="record.alarm_to" boxed :expanded="true" :expand-depth="4" />
        </template>
      </a-table>

      <a-modal
        v-model:visible="state.credModalVisible"
        style="width: 96%; min-width: 400px; overflow-x: scroll"
        :title="state.credModalStatus === 'add' ? '添加' : '编辑'"
        cancel-text="取消"
        ok-text="确定"
        :keyboard="false"
        :mask-closable="false"
        @ok="onSubmit"
        @cancel="resetForm"
      >
        <a-form
          ref="formRef"
          :model="formState"
          :rules="rules"
          :label-col="labelCol"
          :wrapper-col="wrapperCol"
        >
          <a-form-item label="ID" name="id">
            <a-input-number
              v-model:value="formState.id"
              style="width: 200px"
              allow-clear
              placeholder="请输入id"
            />
          </a-form-item>
          <a-form-item label="名称" name="name">
            <a-input v-model:value="formState.name" allow-clear placeholder="请输入name" />
          </a-form-item>
          <a-form-item label="关联规则" name="rule_name">
            <a-select
              v-model:value="formState.rule_name"
              allow-clear
              show-search
              placeholder="请选择规则"
            >
              <a-select-option
                v-for="item in state.ruleDataList"
                :key="item.name"
                :value="item.name"
              >
                {{ item.name }}
              </a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item name="send_type">
            <template #label>
              <span>发送规则</span>
              <a-tooltip placement="top">
                <template #title>
                  选择分label发送，可以根据告警label(例如source，可更改job等)区别配置告警发送人，例如标签source='森华'的发送小王，source='鲁谷'的发送小李，另外可以source设置'default'，给默认接收人，都没有就用common通用的接收配置
                </template>
                <QuestionCircleOutlined />
              </a-tooltip>
            </template>
            <a-select
              v-model:value="formState.send_type"
              allow-clear
              show-search
              placeholder="请选择规则"
            >
              <a-select-option value="common">通用</a-select-option>
              <a-select-option value="label_alarm">分label发送</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item
            v-if="formState.send_type == 'label_alarm'"
            label="依据标签"
            name="label_name"
          >
            <a-select
              v-model:value="formState.label_name"
              allow-clear
              show-search
              allow-create
              placeholder="请选择"
            >
              <a-select-option value="source">source</a-select-option>
              <a-select-option value="job">job</a-select-option>
              <a-select-option value="group">group</a-select-option>
              <a-select-option value="instance">instance</a-select-option>
              <a-select-option value="alertname">alertname</a-select-option>
              <a-select-option value="severity">severity</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item v-if="formState.send_type == 'label_alarm'" label="分标签告警">
            <a-row v-for="(labelItem, ind) in formState.label_send" :key="ind">
              <a-col :span="1">
                <a-button @click="labelNameDel(ind)">
                  <template #icon><MinusCircleOutlined /></template>
                </a-button>
              </a-col>
              <a-col :span="4">
                <a-form-item
                  :label-col="{
                    span: 6,
                  }"
                  :wrapper-col="{
                    span: 18,
                  }"
                  :name="[labelItem, 'label_val']"
                  label="标签值"
                >
                  <a-input
                    v-model:value="labelItem.label_val"
                    allow-clear
                    placeholder="告警标签值，例如森华"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="19">
                <a-form-item
                  :name="[labelItem, 'label_alarm_to']"
                  label="发送方式"
                  :label-col="{
                    span: 4,
                  }"
                  :wrapper-col="{
                    span: 20,
                  }"
                >
                  <div>
                    <a-form-item
                      label="企业微信告警"
                      :label-col="{
                        span: 4,
                      }"
                      :wrapper-col="{
                        span: 20,
                      }"
                    >
                      <a-form
                        :model="labelItem.label_alarm_to?.wechat"
                        :label-col="{
                          span: 8,
                        }"
                        :wrapper-col="{
                          span: 16,
                        }"
                      >
                        <a-space
                          v-for="(labelAlarmItem, labelIndex) in labelItem.label_alarm_to?.wechat"
                          :key="labelIndex"
                          style="margin-bottom: 8px; width: 100%"
                          align="baseline"
                        >
                          <a-form-item :name="[labelAlarmItem, 'robot_url']" label="机器人hook">
                            <a-input
                              v-model:value="labelAlarmItem.robot_url"
                              allow-clear
                              placeholder="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"
                            />
                          </a-form-item>
                          <a-form-item :name="[labelAlarmItem, 'send_to']" label="联系人">
                            <a-select
                              v-model:value="labelAlarmItem.send_to"
                              mode="multiple"
                              style="width: 110px"
                              allow-clear
                              show-search
                              placeholder="请选择联系人"
                            >
                              <a-select-option
                                v-for="item in state.userDataList"
                                :key="item.username"
                                :value="item.username"
                              >
                                {{ item.name }}
                              </a-select-option>
                            </a-select>
                          </a-form-item>
                          <MinusCircleOutlined
                            @click="labelRemoveSend('wechat', labelIndex, ind)"
                          />
                        </a-space>
                        <a-form-item>
                          <a-button type="dashed" block @click="labelAddSend('wechat', ind)">
                            <PlusOutlined />
                            微信告警
                          </a-button>
                        </a-form-item>
                      </a-form>
                    </a-form-item>

                    <a-form-item
                      label="短信告警"
                      :label-col="{
                        span: 4,
                      }"
                      :wrapper-col="{
                        span: 20,
                      }"
                    >
                      <a-form
                        ref="smsFormRef"
                        name="smsForm"
                        :model="labelItem.label_alarm_to?.sms"
                        :label-col="{
                          span: 8,
                        }"
                        :wrapper-col="{
                          span: 16,
                        }"
                      >
                        <a-space
                          v-for="(labelAlarmItem, labelIndex) in labelItem.label_alarm_to?.sms"
                          :key="labelIndex"
                          style="display: flex; margin-bottom: 8px"
                          align="baseline"
                        >
                          <a-form-item :name="[labelAlarmItem, 'send_to']" label="联系人">
                            <a-select
                              v-model:value="labelAlarmItem.send_to"
                              mode="multiple"
                              style="width: 110px"
                              allow-clear
                              show-search
                              placeholder="请选择联系人"
                            >
                              <a-select-option
                                v-for="item in state.userDataList"
                                :key="item.username"
                                :value="item.username"
                              >
                                {{ item.name }}
                              </a-select-option>
                            </a-select>
                          </a-form-item>
                          <MinusCircleOutlined @click="labelRemoveSend('sms', labelIndex, ind)" />
                        </a-space>
                        <a-form-item>
                          <a-button type="dashed" block @click="labelAddSend('sms', ind)">
                            <PlusOutlined />
                            短信告警
                          </a-button>
                        </a-form-item>
                      </a-form>
                    </a-form-item>

                    <a-form-item
                      label="电话告警"
                      :label-col="{
                        span: 4,
                      }"
                      :wrapper-col="{
                        span: 20,
                      }"
                    >
                      <a-form
                        ref="phoneFormRef"
                        name="phoneForm"
                        :model="labelItem.label_alarm_to?.phone"
                        :label-col="{
                          span: 8,
                        }"
                        :wrapper-col="{
                          span: 16,
                        }"
                      >
                        <a-space
                          v-for="(labelAlarmItem, labelIndex) in labelItem.label_alarm_to?.phone"
                          :key="labelIndex"
                          style="display: flex; margin-bottom: 8px"
                          align="baseline"
                        >
                          <a-form-item :name="[labelAlarmItem, 'send_to']" label="联系人">
                            <a-transfer
                              v-model:target-keys="labelAlarmItem.send_to"
                              :data-source="state.userDataListTrasfer"
                              :show-search="true"
                              :filter-option="
                                (inputValue, item) => item.title.labelIndexOf(inputValue) !== -1
                              "
                              :list-style="{
                                width: '250px',
                                height: '300px',
                              }"
                              :titles="['', '已选']"
                            >
                              <template
                                #children="{
                                  direction,
                                  filteredItems,
                                  selectedKeys,
                                  disabled: listDisabled,
                                  onItemSelectAll,
                                  onItemSelect,
                                }"
                              >
                                <a-table
                                  :row-selection="
                                    getRowSelection({
                                      disabled: listDisabled,
                                      selectedKeys,
                                      onItemSelectAll,
                                      onItemSelect,
                                    })
                                  "
                                  :columns="direction === 'left' ? leftColumns : rightColumns"
                                  :data-source="filteredItems"
                                  size="small"
                                  :style="{ pointerEvents: listDisabled ? 'none' : null }"
                                  :custom-row="
                                    ({ key, disabled: itemDisabled }) => ({
                                      onClick: () => {
                                        if (itemDisabled || listDisabled) return;
                                        onItemSelect(key, !selectedKeys.includes(key));
                                      },
                                    })
                                  "
                                />
                              </template>
                            </a-transfer>
                          </a-form-item>
                          <a-form-item>
                            <MinusCircleOutlined
                              @click="labelRemoveSend('phone', labelIndex, ind)"
                            />
                          </a-form-item>
                        </a-space>
                        <a-form-item>
                          <a-button type="dashed" block @click="labelAddSend('phone', ind)">
                            <PlusOutlined />
                            电话告警
                          </a-button>
                        </a-form-item>
                      </a-form>
                    </a-form-item>

                    <a-form-item
                      label="钉钉告警"
                      :label-col="{
                        span: 4,
                      }"
                      :wrapper-col="{
                        span: 20,
                      }"
                    >
                      <a-form
                        ref="dingFormRef"
                        name="dingForm"
                        :model="labelItem.label_alarm_to?.ding"
                        :label-col="{
                          span: 8,
                        }"
                        :wrapper-col="{
                          span: 16,
                        }"
                      >
                        <a-space
                          v-for="(labelAlarmItem, labelIndex) in labelItem.label_alarm_to?.ding"
                          :key="labelIndex"
                          style="display: flex; margin-bottom: 8px"
                          align="baseline"
                        >
                          <a-form-item :name="[labelAlarmItem, 'robot_url']" label="机器人hook">
                            <a-input
                              v-model:value="labelAlarmItem.robot_url"
                              allow-clear
                              placeholder="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"
                            />
                          </a-form-item>
                          <a-form-item :name="[labelAlarmItem, 'send_to']" label="联系人">
                            <a-select
                              v-model:value="labelAlarmItem.send_to"
                              mode="multiple"
                              style="width: 110px"
                              allow-clear
                              show-search
                              placeholder="请选择联系人"
                            >
                              <a-select-option
                                v-for="item in state.userDataList"
                                :key="item.username"
                                :value="item.username"
                              >
                                {{ item.name }}
                              </a-select-option>
                            </a-select>
                          </a-form-item>
                          <a-form-item>
                            <MinusCircleOutlined
                              @click="labelRemoveSend('ding', labelIndex, ind)"
                            />
                          </a-form-item>
                        </a-space>
                        <a-form-item>
                          <a-button type="dashed" block @click="labelAddSend('ding', ind)">
                            <PlusOutlined />
                            钉钉告警
                          </a-button>
                        </a-form-item>
                      </a-form>
                    </a-form-item>

                    <a-form-item
                      label="邮件告警"
                      :label-col="{
                        span: 4,
                      }"
                      :wrapper-col="{
                        span: 20,
                      }"
                    >
                      <a-form
                        ref="emailFormRef"
                        name="emailForm"
                        :model="labelItem.label_alarm_to?.email"
                        :label-col="{
                          span: 8,
                        }"
                        :wrapper-col="{
                          span: 16,
                        }"
                      >
                        <a-space
                          v-for="(labelAlarmItem, labelIndex) in labelItem.label_alarm_to?.email"
                          :key="labelIndex"
                          style="display: flex; margin-bottom: 8px"
                          align="baseline"
                        >
                          <a-form-item :name="[labelAlarmItem, 'send_email']">
                            <template #label>
                              <span>发送端邮箱</span>
                              <a-tooltip placement="top" title="host|#|uname|#|pwd">
                                <QuestionCircleOutlined />
                              </a-tooltip>
                            </template>

                            <a-input
                              v-model:value="labelAlarmItem.send_email"
                              allow-clear
                              placeholder="默认为ccr_paas_postman,host|#|uname|#|pwd|#|from"
                            />
                          </a-form-item>
                          <a-form-item :name="[labelAlarmItem, 'send_to']" label="联系人">
                            <a-select
                              v-model:value="labelAlarmItem.send_to"
                              mode="multiple"
                              style="width: 110px"
                              allow-clear
                              show-search
                              placeholder="请选择联系人"
                            >
                              <a-select-option
                                v-for="item in state.userDataList"
                                :key="item.username"
                                :value="item.username"
                              >
                                {{ item.name }}
                              </a-select-option>
                            </a-select>
                          </a-form-item>
                          <MinusCircleOutlined @click="labelRemoveSend('email', labelIndex, ind)" />
                        </a-space>
                        <a-form-item>
                          <a-button type="dashed" block @click="labelAddSend('email', ind)">
                            <PlusOutlined />
                            邮件告警
                          </a-button>
                        </a-form-item>
                      </a-form>
                    </a-form-item>
                  </div>
                </a-form-item>
              </a-col>
            </a-row>
            <!-- </a-space> -->

            <a-form-item>
              <a-button type="dashed" block @click="labelNameAdd()">
                <PlusOutlined />
                添加标签值
              </a-button>
            </a-form-item>
          </a-form-item>

          <div v-if="formState.send_type == 'common'">
            <a-form-item>
              <template #label>
                <span>企业微信告警</span>
                <a-tooltip placement="top">
                  <template #title>
                    <a
                      target="_blank"
                      href="https://developer.work.weixin.qq.com/document/path/99110"
                      >api接口</a
                    >
                  </template>
                  <QuestionCircleOutlined />
                </a-tooltip>
              </template>
              <a-form
                ref="wxFormRef"
                name="wxForm"
                :model="formState.alarm_to?.wechat"
                :label-col="{
                  span: 8,
                }"
                :wrapper-col="{
                  span: 16,
                }"
              >
                <a-space
                  v-for="(alarmItem, index) in formState.alarm_to?.wechat"
                  :key="index"
                  style="display: flex; margin-bottom: 8px"
                  align="baseline"
                >
                  <a-form-item :name="[alarmItem, 'robot_url']" label="机器人hook">
                    <a-input
                      v-model:value="alarmItem.robot_url"
                      allow-clear
                      placeholder="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"
                    />
                  </a-form-item>
                  <a-form-item :name="[alarmItem, 'send_to']" label="联系人">
                    <a-select
                      v-model:value="alarmItem.send_to"
                      mode="multiple"
                      style="width: 110px"
                      allow-clear
                      show-search
                      placeholder="请选择联系人"
                    >
                      <a-select-option
                        v-for="item in state.userDataList"
                        :key="item.username"
                        :value="item.username"
                      >
                        {{ item.name }}
                      </a-select-option>
                    </a-select>
                  </a-form-item>
                  <MinusCircleOutlined @click="removeWx(alarmItem)" />
                </a-space>
                <a-form-item>
                  <a-button type="dashed" block @click="addWx">
                    <PlusOutlined />
                    微信告警
                  </a-button>
                </a-form-item>
              </a-form>
            </a-form-item>

            <a-form-item label="短信告警">
              <a-form
                ref="smsFormRef"
                name="smsForm"
                :model="formState.alarm_to?.sms"
                :label-col="{
                  span: 8,
                }"
                :wrapper-col="{
                  span: 16,
                }"
              >
                <a-space
                  v-for="(alarmItem, index) in formState.alarm_to?.sms"
                  :key="index"
                  style="display: flex; margin-bottom: 8px"
                  align="baseline"
                >
                  <a-form-item :name="[alarmItem, 'send_to']" label="联系人">
                    <a-select
                      v-model:value="alarmItem.send_to"
                      mode="multiple"
                      style="width: 110px"
                      allow-clear
                      show-search
                      placeholder="请选择联系人"
                    >
                      <a-select-option
                        v-for="item in state.userDataList"
                        :key="item.username"
                        :value="item.username"
                      >
                        {{ item.name }}
                      </a-select-option>
                    </a-select>
                  </a-form-item>
                  <MinusCircleOutlined @click="removeSms(alarmItem)" />
                </a-space>
                <a-form-item>
                  <a-button type="dashed" block @click="addSms">
                    <PlusOutlined />
                    短信告警
                  </a-button>
                </a-form-item>
              </a-form>
            </a-form-item>

            <a-form-item label="电话告警">
              <a-form
                ref="phoneFormRef"
                name="phoneForm"
                :model="formState.alarm_to?.phone"
                :label-col="{
                  span: 8,
                }"
                :wrapper-col="{
                  span: 16,
                }"
              >
                <a-space
                  v-for="(alarmItem, index) in formState.alarm_to?.phone"
                  :key="index"
                  style="display: flex; margin-bottom: 8px"
                  align="baseline"
                >
                  <a-form-item :name="[alarmItem, 'send_to']" label="联系人">
                    <!-- <a-select
                    v-model:value="alarmItem.send_to"
                    mode="multiple"
                    style="width: 110px"
                    allow-clear
                    show-search
                    placeholder="请选择联系人"
                  >
                    <a-select-option
                      v-for="item in state.userDataList"
                      :key="item.username"
                      :value="item.username"
                    >
                      {{ item.name }}
                    </a-select-option>
                  </a-select> -->

                    <a-transfer
                      v-model:target-keys="alarmItem.send_to"
                      :data-source="state.userDataListTrasfer"
                      :show-search="true"
                      :filter-option="(inputValue, item) => item.title.indexOf(inputValue) !== -1"
                      :list-style="{
                        width: '250px',
                        height: '300px',
                      }"
                      :titles="['', '已选']"
                    >
                      <template
                        #children="{
                          direction,
                          filteredItems,
                          selectedKeys,
                          disabled: listDisabled,
                          onItemSelectAll,
                          onItemSelect,
                        }"
                      >
                        <a-table
                          :row-selection="
                            getRowSelection({
                              disabled: listDisabled,
                              selectedKeys,
                              onItemSelectAll,
                              onItemSelect,
                            })
                          "
                          :columns="direction === 'left' ? leftColumns : rightColumns"
                          :data-source="filteredItems"
                          size="small"
                          :style="{ pointerEvents: listDisabled ? 'none' : null }"
                          :custom-row="
                            ({ key, disabled: itemDisabled }) => ({
                              onClick: () => {
                                if (itemDisabled || listDisabled) return;
                                onItemSelect(key, !selectedKeys.includes(key));
                              },
                            })
                          "
                        />
                      </template>
                    </a-transfer>
                  </a-form-item>
                  <a-form-item>
                    <MinusCircleOutlined @click="removePhone(alarmItem)" />
                  </a-form-item>
                </a-space>
                <a-form-item>
                  <a-button type="dashed" block @click="addPhone">
                    <PlusOutlined />
                    电话告警
                  </a-button>
                </a-form-item>
              </a-form>
            </a-form-item>

            <a-form-item>
              <template #label>
                <span>钉钉告警</span>
                <a-tooltip placement="top">
                  <template #title>
                    <a
                      target="_blank"
                      href="https://open.dingtalk.com/document/orgapp/message-types-and-data-format"
                      >api接口</a
                    >
                  </template>
                  <QuestionCircleOutlined />
                </a-tooltip>
              </template>
              <a-form
                ref="dingFormRef"
                name="dingForm"
                :model="formState.alarm_to?.ding"
                :label-col="{
                  span: 8,
                }"
                :wrapper-col="{
                  span: 16,
                }"
              >
                <a-space
                  v-for="(alarmItem, index) in formState.alarm_to?.ding"
                  :key="index"
                  style="display: flex; margin-bottom: 8px"
                  align="baseline"
                >
                  <a-form-item :name="[alarmItem, 'robot_url']" label="机器人hook">
                    <a-input
                      v-model:value="alarmItem.robot_url"
                      allow-clear
                      placeholder="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"
                    />
                  </a-form-item>
                  <a-form-item :name="[alarmItem, 'send_to']" label="联系人">
                    <a-select
                      v-model:value="alarmItem.send_to"
                      mode="multiple"
                      style="width: 110px"
                      allow-clear
                      show-search
                      placeholder="请选择联系人"
                    >
                      <a-select-option
                        v-for="item in state.userDataList"
                        :key="item.username"
                        :value="item.username"
                      >
                        {{ item.name }}
                      </a-select-option>
                    </a-select>
                  </a-form-item>
                  <a-form-item>
                    <MinusCircleOutlined @click="removeDing(alarmItem)" />
                  </a-form-item>
                </a-space>
                <a-form-item>
                  <a-button type="dashed" block @click="addDing">
                    <PlusOutlined />
                    钉钉告警
                  </a-button>
                </a-form-item>
              </a-form>
            </a-form-item>

            <a-form-item label="邮件告警">
              <a-form
                ref="emailFormRef"
                name="emailForm"
                :model="formState.alarm_to?.email"
                :label-col="{
                  span: 8,
                }"
                :wrapper-col="{
                  span: 16,
                }"
              >
                <a-space
                  v-for="(alarmItem, index) in formState.alarm_to?.email"
                  :key="index"
                  style="display: flex; margin-bottom: 8px"
                  align="baseline"
                >
                  <a-form-item :name="[alarmItem, 'send_email']">
                    <template #label>
                      <span>发送端邮箱</span>
                      <a-tooltip placement="top" title="host|#|uname|#|pwd">
                        <QuestionCircleOutlined />
                      </a-tooltip>
                    </template>

                    <a-input
                      v-model:value="alarmItem.send_email"
                      allow-clear
                      placeholder="默认为ccr_paas_postman,host|#|uname|#|pwd|#|from"
                    />
                  </a-form-item>
                  <a-form-item :name="[alarmItem, 'send_to']" label="联系人">
                    <a-select
                      v-model:value="alarmItem.send_to"
                      mode="multiple"
                      style="width: 110px"
                      allow-clear
                      show-search
                      placeholder="请选择联系人"
                    >
                      <a-select-option
                        v-for="item in state.userDataList"
                        :key="item.username"
                        :value="item.username"
                      >
                        {{ item.name }}
                      </a-select-option>
                    </a-select>
                  </a-form-item>
                  <MinusCircleOutlined @click="removeEmail(alarmItem)" />
                </a-space>
                <a-form-item>
                  <a-button type="dashed" block @click="addEmail">
                    <PlusOutlined />
                    邮件告警
                  </a-button>
                </a-form-item>
              </a-form>
            </a-form-item>
          </div>

          <a-form-item label="告警开始" name="alert_start">
            <a-input
              v-model:value="formState.alert_start"
              allow-clear
              placeholder="08:00,代表从早8以后才会发送"
            />
          </a-form-item>
          <a-form-item label="告警结束" name="alert_end">
            <a-input
              v-model:value="formState.alert_end"
              allow-clear
              placeholder="21:00,代表从晚8以前才会发送"
            />
          </a-form-item>
          <a-form-item label="备注" name="desc">
            <a-input v-model:value="formState.desc" allow-clear placeholder="备注" />
          </a-form-item>
        </a-form>
      </a-modal>

      <div
        class="float-right"
        style="width: 100%; padding: 10px 0; white-space: nowrap; overflow-x: scroll"
      >
        <a-pagination
          size="md"
          :show-total="(total) => `共 ${state.total} 条数据`"
          :current="state.page"
          :page-size-options="state.pageSizeOptions"
          :total="state.total"
          show-size-changer
          :page-size="state.size"
          show-less-items
          align="right"
          @change="onChange"
        >
          <template #buildOptionText="props">
            <span v-if="props.value !== '50'">{{ props.value }}条/页</span>
            <span v-if="props.value === '50'">全部</span>
          </template>
        </a-pagination>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import 'vue3-json-viewer/dist/index.css';
  import { inject, onMounted, reactive, ref } from 'vue';
  import { JsonViewer } from 'vue3-json-viewer';
  import { MinusCircleOutlined, PlusOutlined, QuestionCircleOutlined } from '@ant-design/icons-vue';
  import { getDataListByPage as getUserList } from '@/api/alarm/user';
  import { getDataListByPage as getRuleList } from '@/api/alarm/rule';
  import { getDataListByPage, createData, deleteData, updateData } from '@/api/alarm/config';
  defineOptions({
    name: 'AlarmConfig',
  });
  type tableColumn = Record<string, string>;
  const leftTableColumns = [
    {
      dataIndex: 'title',
      title: 'Name',
    },
  ];
  const rightTableColumns = [
    {
      dataIndex: 'title',
      title: 'Name',
    },
  ];
  const leftColumns = ref<tableColumn[]>(leftTableColumns);
  const rightColumns = ref<tableColumn[]>(rightTableColumns);
  const getRowSelection = ({
    disabled,
    selectedKeys,
    onItemSelectAll,
    onItemSelect,
  }: Record<string, any>) => {
    return {
      getCheckboxProps: (item: Record<string, string | boolean>) => ({
        disabled: disabled || item.disabled,
      }),
      onSelectAll(selected: boolean, selectedRows: Record<string, string | boolean>[]) {
        const treeSelectedKeys = selectedRows
          .filter((item) => !item.disabled)
          .map(({ key }) => key);
        onItemSelectAll(treeSelectedKeys, selected);
      },
      onSelect({ key }: Record<string, string>, selected: boolean) {
        onItemSelect(key, selected);
      },
      selectedRowKeys: selectedKeys,
    };
  };
  const activeKey = ref(['1']);
  const typeColor = {
    wechat: 'cyan',
    phone: 'orange',
    sms: 'pink',
    email: 'green',
    ding: 'blue',
  };
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
    },
    {
      title: '名称',
      dataIndex: 'name',
    },
    {
      title: '关联规则',
      dataIndex: 'rule_name',
    },
    {
      title: '方式',
      dataIndex: 'alarm_detail',
    },
    {
      title: '告警开始',
      dataIndex: 'alert_start',
    },
    {
      title: '告警结束',
      dataIndex: 'alert_end',
    },
    {
      title: '修改人',
      dataIndex: 'updated_by',
    },
    {
      title: '修改时间',
      dataIndex: 'updated_at',
    },

    {
      title: '描述',
      dataIndex: 'desc',
    },
    {
      title: '操作',
      dataIndex: 'action',
    },
  ];

  let selectedRowKeys;
  const state = reactive({
    selectedRows: [],
    selectedRowKeys,
    loading: false,
    data: [],
    size: 10,
    page: 1,
    total: 0,
    pageSizeOptions: ['5', '10', '15', '20'],
    credModalVisible: false,
    credModalStatus: 'add',
    searchVal: '',
    searchID: '',
    searchloading: false,
    ruleDataList: [],
    userDataList: [],
    userDataListTrasfer: [],
  });
  const labelCol = {
    span: 4,
  };
  const wrapperCol = {
    span: 20,
  };
  const addNewData = () => {
    // formState.email = undefined;
    Object.assign(formState, {
      id: '',
      rule_name: '',
      name: '',
      email: '',
      desc: '',
      alarm_to: { wechat: [], sms: [], phone: [], ding: [], email: [] },
    });
    state.credModalStatus = 'add';
    state.credModalVisible = true;
  };

  const formRef = ref();
  const wxFormRef = ref();
  const emailFormRef = ref();
  const smsFormRef = ref();
  const phoneFormRef = ref();
  const dingFormRef = ref();

  const labelNameDel = (index) => {
    try {
      formState.label_send.splice(index, 1);
    } catch (e) {
      console.log('labelNameDel fail', e);
    }
  };
  const labelNameAdd = () => {
    formState.label_send.push({
      label_val: '',
      label_alarm_to: { wechat: [], sms: [], phone: [], ding: [], email: [] },
    });
  };
  const labelRemoveSend = (sendType, innerIndex, index) => {
    try {
      formState.label_send[index]['label_alarm_to'][sendType].splice(innerIndex, 1);
    } catch (e) {
      console.log('labelRemoveSend fail', e);
    }
  };
  const labelAddSend = (sendType, index) => {
    if (sendType === 'wechat') {
      formState.label_send[index]['label_alarm_to'][sendType].push({
        robot_url: '',
        send_to: [],
      });
    } else if (sendType === 'sms') {
      formState.label_send[index]['label_alarm_to'][sendType].push({
        send_to: [],
      });
    } else if (sendType === 'phone') {
      formState.label_send[index]['label_alarm_to'][sendType].push({
        send_to: [],
      });
    } else if (sendType === 'ding') {
      formState.label_send[index]['label_alarm_to'][sendType].push({
        robot_url: '',
        send_to: [],
      });
    } else if (sendType === 'email') {
      formState.label_send[index]['label_alarm_to'][sendType].push({
        send_email: '',
        send_to: [],
      });
    }
  };
  const removeWx = (item) => {
    if (formState.alarm_to?.wechat) {
      const index = formState.alarm_to.wechat.indexOf(item);
      if (index !== -1) {
        formState.alarm_to.wechat.splice(index, 1);
      }
    }
  };
  const addWx = () => {
    if (formState.alarm_to?.wechat) {
      formState.alarm_to.wechat.push({
        robot_url: '',
        send_to: [],
        // timestamp: Date.now(),
      });
    }
  };
  const removeSms = (item) => {
    if (formState.alarm_to?.sms) {
      const index = formState.alarm_to.sms.indexOf(item);
      if (index !== -1) {
        formState.alarm_to.sms.splice(index, 1);
      }
    }
  };
  const addSms = () => {
    if (formState.alarm_to?.sms) {
      formState.alarm_to.sms.push({
        send_to: [],
        // timestamp: Date.now(),
      });
    }
  };

  const removePhone = (item) => {
    if (formState.alarm_to?.phone) {
      const index = formState.alarm_to.phone.indexOf(item);
      if (index !== -1) {
        formState.alarm_to.phone.splice(index, 1);
      }
    }
  };
  const addPhone = () => {
    if (formState.alarm_to?.phone) {
      formState.alarm_to.phone.push({
        send_to: [],
        // timestamp: Date.now(),
      });
    }
  };

  const removeDing = (item) => {
    if (formState.alarm_to?.ding) {
      const index = formState.alarm_to.ding.indexOf(item);
      if (index !== -1) {
        formState.alarm_to.ding.splice(index, 1);
      }
    }
  };
  const addDing = () => {
    if (formState.alarm_to?.ding) {
      formState.alarm_to.ding.push({
        robot_url: '',
        send_to: [],
        // timestamp: Date.now(),
      });
    }
  };

  const removeEmail = (item) => {
    if (formState.alarm_to?.email) {
      const index = formState.alarm_to.email.indexOf(item);
      if (index !== -1) {
        formState.alarm_to.email.splice(index, 1);
      }
    }
  };
  const addEmail = () => {
    if (formState.alarm_to?.email) {
      formState.alarm_to.email.push({
        send_email: '',
        send_to: [],
        // timestamp: Date.now(),
      });
    }
  };
  const generateFormState = () => {
    return {
      id: '',
      rule_name: '',
      name: '',
      email: '',
      desc: '',
      alarm_to: { wechat: [], sms: [], phone: [], ding: [], email: [] },
      send_type: 'common',
      label_name: 'source',
      label_send: [],
    };
  };
  const formState = reactive(generateFormState());
  const rules = {
    id: [
      {
        required: true,
        message: '请输入id',
        trigger: 'blur',
      },
      { pattern: /(^\S)((.)*\S)?(\S*$)/, message: '前后不能有空格' },
    ],
    name: [
      {
        required: true,
        message: '请输入name',
        trigger: 'blur',
      },
      { pattern: /(^\S)((.)*\S)?(\S*$)/, message: '前后不能有空格' },
    ],
  };

  const onSubmit = () => {
    formRef.value.validate().then(() => {
      const params = Object.fromEntries(Object.entries(formState));
      if (state.credModalStatus == 'add') {
        params.operate = 'add';

        createData(params).finally(() => {
          state.credModalVisible = false;
          resetForm();
          getDataList();
        });
      } else {
        updateData(params).finally(() => {
          state.credModalVisible = false;
          resetForm();
          getDataList();
        });
      }
    });
  };

  const resetForm = () => {
    Object.assign(formState, generateFormState());
  };
  const message = inject('$message');
  // 获取信息
  const getDataList = async () => {
    const params = {
      page: state.page,
      size: state.size,
      searchVal: state.searchVal,
      id: state.searchID,
    };
    state.loading = true;
    await getDataListByPage(params).then(
      (res) => ((state.data = res.data), (state.total = res.count), (state.loading = false)),
    );

    // state.size = data.size
  };
  // 翻页
  const onChange = async (pageNumber, size) => {
    state.page = pageNumber;
    state.size = size;
    await getDataList();
  };

  const rowSelection = {
    onChange: (selectedRowKeys, selectedRows) => {
      state.selectedRows = selectedRows;
      state.selectedRowKeys = selectedRowKeys;
    },
  };
  //模糊查询
  const searchDatalist = async () => {
    // state.searchVal = searchText;
    state.searchloading = true;
    await getDataList();
    state.searchloading = false;
  };
  //Id查询
  // const searchIdDatalist = async () => {
  //   state.searchID = searchText;
  //   state.searchloading = true;
  //   await getDataList();
  //   state.searchloading = false;
  // };
  // 批量删除
  const removeData = async () => {
    const deleteIds = [];
    for (let i = 0; i < state.selectedRowKeys.length; i++) {
      deleteIds.push(state.selectedRowKeys[i]);
    }
    await deleteData({ deleteIds }).finally(() => {
      state.selectedRows = [];
      getDataList();
    });
  };

  // 查看详情
  const rowEdit = (record) => {
    Object.assign(formState, record);
    state.credModalStatus = 'update';
    state.credModalVisible = true;
  };
  const getRuleData = () => {
    getRuleList({ isSelect: true }).then((res) => (state.ruleDataList = res.data));
  };
  const getUserData = () => {
    getUserList({ isSelect: true }).then((res) => {
      state.userDataList = res.data;
      state.userDataListTrasfer = [];
      state.userDataList.map((item) => {
        state.userDataListTrasfer.push({
          key: item.username,
          title: item.name + item.username,
          description: item.username,
        });
      });
    });
  };

  onMounted(() => {
    getDataList();
    getRuleData();
    getUserData();
  });
</script>

<style>
  .a-class {
    color: #1890ff;
  }
</style>
