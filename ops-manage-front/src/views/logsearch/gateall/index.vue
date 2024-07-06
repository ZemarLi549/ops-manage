<template>
  <div class="screen">
    <a-row :gutter="4">
      <FilterForm @searchClick="searchClick" />
    </a-row>

    <a-row :gutter="4" style="margin-bottom: 4px" type="flex" justify="space-around" align="middle">
      <a-col :xs="12" :sm="12" :md="6">
        <div class="block-box gutter-row-2">
          <Title>请求总数(PV)</Title>
          <a-spin :spinning="state.tableLoading">
            <p class="digitshow"
              ><countTo :start-val="0" :end-val="state.totalCnt" :duration="2000"
            /></p>
          </a-spin>
        </div>
      </a-col>
      <a-col :xs="12" :sm="12" :md="6">
        <div class="block-box gutter-row-2">
          <Title>客户端数(UV)</Title>
          <a-spin :spinning="state.clientPieLoading">
            <p class="digitshow"
              ><countTo :start-val="0" :end-val="state.uvCnt" :duration="2000"
            /></p>
          </a-spin>
        </div>
      </a-col>
      <a-col :xs="12" :sm="12" :md="6">
        <div class="block-box gutter-row-2">
          <Title>错误数(5xx)/错误率</Title>
          <a-spin :spinning="state.tableLoading">
            <p class="digitshow" style="color: #ce5050"
              ><countTo :start-val="0" :end-val="state.errCnt" :duration="2000" />/<countTo
                :start-val="0"
                :end-val="state.errRate"
                :duration="2000"
                :decimals="3"
              />
            </p>
          </a-spin>
        </div>
      </a-col>
      <a-col :xs="12" :sm="12" :md="6">
        <div class="block-box gutter-row-2">
          <Title>响应时间秒(50分位/90分位/最长)</Title>
          <a-spin :spinning="state.tableLoading">
            <p class="digitshow"
              ><countTo
                :start-val="0"
                :end-val="state.fiveresp"
                :duration="2000"
                :decimals="3"
              />/<countTo
                :start-val="0"
                :end-val="state.nineresp"
                :duration="2000"
                :decimals="3"
              />/<countTo :start-val="0" :end-val="state.maxresp" :duration="2000" :decimals="3" />
            </p>
          </a-spin>
        </div>
      </a-col>
    </a-row>
    <a-row :gutter="4" style="margin-bottom: 4px" type="flex" justify="space-around" align="middle">
      <a-col :xs="24" :sm="24" :md="12">
        <a-spin :spinning="state.statusLineLoading">
          <div class="block-box gutter-row-3">
            <Title>状态码分布</Title>

            <MultiLine :show-data="statusLineData"></MultiLine>
          </div>
        </a-spin>
      </a-col>
      <a-col :xs="24" :sm="24" :md="12">
        <a-spin :spinning="state.respLineLoading">
          <div class="block-box gutter-row-3">
            <Title>响应时间分布</Title>
            <MultiLine :show-data="respLineData"></MultiLine>
          </div>
        </a-spin>
      </a-col>
    </a-row>
    <a-row :gutter="4" style="margin-bottom: 4px" type="flex" justify="space-around" align="middle">
      <a-col :xs="24" :sm="24" :md="12">
        <a-spin :spinning="state.netLineLoading">
          <div class="block-box gutter-row-3">
            <Title>流入流出量（Mb）</Title>
            <MultiLine :show-data="netLineData"></MultiLine>
          </div>
        </a-spin>
      </a-col>
      <a-col :xs="24" :sm="24" :md="12">
        <a-spin :spinning="state.methodStLoading">
          <div class="block-box gutter-row-3">
            <Title>请求类型分布</Title>
            <MultiLine :show-data="methodStLineData"></MultiLine>
          </div>
        </a-spin>
      </a-col>
    </a-row>
    <a-row :gutter="4" style="margin-bottom: 4px" type="flex" justify="space-around" align="middle">
      <a-col :xs="24" :sm="24" :md="12" :lg="6">
        <a-spin :spinning="state.respPieLoading">
          <div class="block-box gutter-row-4">
            <Title>响应时间占比</Title>
            <Multipie :show-data="respPieData" />
          </div>
        </a-spin>
      </a-col>
      <a-col :xs="24" :sm="24" :md="12" :lg="6">
        <a-spin :spinning="state.statusPieLoading">
          <div class="block-box gutter-row-4">
            <Title>状态码占比</Title>
            <Multipie :show-data="statusPieData" />
          </div>
        </a-spin>
      </a-col>
      <a-col :xs="24" :sm="24" :md="12" :lg="6">
        <a-spin :spinning="state.methodPieLoading">
          <div class="block-box gutter-row-4">
            <Title>请求类型占比</Title>
            <Multipie :show-data="methodPieData" />
          </div>
        </a-spin>
      </a-col>
      <a-col :xs="24" :sm="24" :md="12" :lg="6">
        <a-spin :spinning="state.clientPieLoading">
          <div class="block-box gutter-row-4">
            <Title>客户端ip占比</Title>
            <ClientPie :show-data="clientPieData" />
          </div>
        </a-spin>
      </a-col>
    </a-row>
    <a-row :gutter="4" style="margin-bottom: 4px" type="flex" justify="space-around" align="middle">
      <div class="block-box gutter-row-5">
        <Title>各uri总览表</Title>
        <div style="margin: 10px 10px; width: 220px">
          <a-input-search
            v-model:value="state.searchVal"
            placeholder="模糊查询"
            enter-button="搜索"
            allow-clear
            @search="searchDatalist"
          />
        </div>
        <a-table
          size="default"
          :scroll="{ y: 600, x: 1100 }"
          :columns="columns"
          :data-source="
            state.dataSource.slice(
              (state.current - 1) * state.pageSize,
              state.current * state.pageSize,
            )
          "
          :loading="state.tableLoading"
          :pagination="false"
          @change="handleTableChange"
        >
        </a-table>
        <a-pagination
          :current="state.current"
          size="middle"
          :page-size="state.pageSize"
          :page-size-options="state.sizeList"
          :total="state.dataSource.length"
          show-size-changer
          show-quick-jumper
          :show-total="(total) => `共 ${total} 条`"
          @change="pageNumberChange"
        />
      </div>
    </a-row>
  </div>
</template>

<script setup lang="ts">
  import { onMounted, reactive } from 'vue';
  import MultiLine from './components/multiline.vue';
  import Multipie from './components/multipie.vue';
  import FilterForm from './components/filter.vue';
  import ClientPie from './components/clientpie.vue';
  import countTo from '@/components/vue3-count-to/vue-countTo';
  import {
    hostTable,
    statusLine,
    reqAllLine,
    netAllLine,
    methodStLine,
    respPie,
    commonPie,
    clientIpPie,
  } from '@/api/log/gateall';

  import Title from '@/components/cardtitle/Title.vue';
  defineOptions({
    name: 'GateAll',
  });
  const columns = [
    {
      title: '接口路径',
      dataIndex: 'path',
      // fixed: 'left',
      width: 250,
    },
    {
      title: 'PV',
      dataIndex: 'totalCount',
      sorter: true,
    },
    // {
    //   title: '均衡UV',
    //   dataIndex: 'uv',
    //   sorter: true,
    // },

    {
      title: '错误数5xx',
      dataIndex: 'errorCount',
      sorter: true,
    },
    {
      title: '错误率',
      dataIndex: 'errorRatio',
      sorter: true,
    },
    {
      title: '50分位',
      dataIndex: 'fiveResp',
      sorter: true,
    },
    {
      title: '90分位',
      dataIndex: 'nineResp',
      sorter: true,
    },
    {
      title: '最大请求时间',
      dataIndex: 'maxResp',
      sorter: true,
    },
    {
      title: '流出流量(M)',
      dataIndex: 'net_out',
      sorter: true,
    },
    {
      title: '流入流量(M)',
      dataIndex: 'net_in',
      sorter: true,
    },
  ];
  const sortAscByKey = (arr, key) => {
    return arr.sort(function (a, b) {
      const x = a[key];
      const y = b[key];
      return x < y ? -1 : x > y ? 1 : 0;
    });
  };
  const sortDescByKey = (arr, key) => {
    return arr.sort(function (a, b) {
      const x = a[key];
      const y = b[key];
      return x > y ? -1 : x < y ? 1 : 0;
    });
  };
  const handleTableChange = (pagination, filters, sorter) => {
    const filterList = state.backDataSource;
    if (sorter.order === 'descend') {
      state.dataSource = sortDescByKey(filterList, sorter.column.dataIndex);
    } else if (sorter.order === 'ascend') {
      state.dataSource = sortAscByKey(filterList, sorter.column.dataIndex);
    }
  };
  const tableRes = (table, array) => {
    const search = state.searchVal.toLowerCase();
    if (search) {
      // filter() 方法创建一个新的数组，新数组中的元素是通过检查指定数组中符合条件的所有元素。
      // 注意： filter() 不会对空数组进行检测。
      // 注意： filter() 不会改变原始数组。
      return table.filter((data) => {
        // console.log('22',data)
        // some() 方法用于检测数组中的元素是否满足指定条件;
        // some() 方法会依次执行数组的每个元素：
        // 如果有一个元素满足条件，则表达式返回true , 剩余的元素不会再执行检测;
        // 如果没有满足条件的元素，则返回false。
        // 注意： some() 不会对空数组进行检测。
        // 注意： some() 不会改变原始数组。
        return Object.keys(data).some((key) => {
          // indexOf() 返回某个指定的字符在某个字符串中首次出现的位置，如果没有找到就返回-1；
          // 该方法对大小写敏感！所以之前需要toLowerCase()方法将所有查询到内容变为小写。
          if (array) {
            if (array.indexOf(key) === -1) {
              // console.log('11',array.indexOf(key))
              return String(data[key]).toLowerCase().indexOf(search) > -1;
            }
          } else {
            return String(data[key]).toLowerCase().indexOf(search) > -1;
          }
        });
      });
    }
    return table;
  };
  const searchDatalist = () => {
    state.dataSource = tableRes(state.backDataSource);
  };
  const state = reactive({
    isday: 'no',
    totalCnt: 0,
    errCnt: 0,
    errRate: 0.0,
    uvCnt: 0,
    maxresp: 0,
    fiveresp: 0,
    nineresp: 0,
    clientPieLoading: false,
    reqCountLoading: false,
    statusPieLoading: false,
    methodPieLoading: false,
    respPieLoading: false,
    methodStLoading: false,
    netLineLoading: false,
    statusLineLoading: false,
    respLineLoading: false,
    searchVal: '',
    tableLoading: false,
    dataSource: [],
    backDataSource: [],
    sizeList: ['5', '10', '20', '30'], //一页能显示条数
    pageSize: 5, //当前页显示多少条
    current: 1, //当前页
    total: 0, //总条数,在获取后台数据时将数组的length赋值给total
  });
  const trigHostTable = (params) => {
    state.tableLoading = true;
    state.backDataSource = [];
    state.dataSource = [];

    state.totalCnt = 0;
    state.maxresp = 0;
    state.fiveresp = 0;
    state.nineresp = 0;
    state.errCnt = 0;
    state.errRate = 0;
    hostTable(params).then((res) => {
      state.tableLoading = false;
      state.backDataSource = res?.data;
      state.dataSource = res?.data;
      state.errRate = res?.appendData.errRate;
      state.totalCnt = res?.appendData.totalCnt;
      state.errCnt = res?.appendData.errCnt;
      state.fiveresp = res?.appendData.fiveresp;
      state.nineresp = res?.appendData.nineresp;
      state.maxresp = res?.appendData.maxresp;
    });
  };
  const trigStatusLine = (params) => {
    state.statusLineLoading = true;
    statusLineData.xList = [];
    statusLineData.dataList = [];
    statusLine(params).then((res) => {
      state.statusLineLoading = false;
      statusLineData.xList = res.xList;
      statusLineData.dataList = res.dataList;
    });
  };
  const trigReqAllLine = (params) => {
    state.respLineLoading = true;
    respLineData.xList = [];
    respLineData.dataList = [];
    reqAllLine(params).then((res) => {
      state.respLineLoading = false;
      respLineData.xList = res.xList;
      respLineData.dataList = res.dataList;
    });
  };
  const trigNetAllLine = (params) => {
    state.netLineLoading = true;
    netLineData.xList = [];
    netLineData.dataList = [];
    netAllLine(params).then((res) => {
      state.netLineLoading = false;
      netLineData.xList = res.xList;
      netLineData.dataList = res.dataList;
    });
  };
  const trigMethodStlLine = (params) => {
    state.methodStLoading = true;
    methodStLineData.xList = [];
    methodStLineData.dataList = [];
    methodStLine(params).then((res) => {
      state.methodStLoading = false;
      methodStLineData.xList = res.xList;
      methodStLineData.dataList = res.dataList;
    });
  };
  const trigRespPie = (params) => {
    state.respPieLoading = true;
    respPieData.dataList = [];
    respPie(params).then((res) => {
      state.respPieLoading = false;
      respPieData.dataList = res.dataList;
    });
  };
  const trigStatusPie = (params) => {
    state.statusPieLoading = true;
    statusPieData.dataList = [];
    params.fieldKey = 'status';
    commonPie(params).then((res) => {
      state.statusPieLoading = false;
      statusPieData.dataList = res.dataList;
    });
  };
  const trigMethodPie = (params) => {
    state.methodPieLoading = true;
    methodPieData.dataList = [];
    params.fieldKey = 'request_method';
    commonPie(params).then((res) => {
      state.methodPieLoading = false;
      methodPieData.dataList = res.dataList;
    });
  };
  //实时获取uvcnt
  const trigClientPie = (params) => {
    state.clientPieLoading = true;
    clientPieData.dataList = [];
    clientIpPie(params).then((res) => {
      state.clientPieLoading = false;
      clientPieData.dataList = res.dataList;
      state.uvCnt = res.dataList.length;
    });
  };

  //实时获取domain five nine resp
  // const trigLiveFiveLine = (params) => {
  //   state.reqCountLoading = true;
  //   state.fiveresp = 0;
  //   state.nineresp = 0;
  //   fiveNineResp(params).then((res) => {
  //     state.reqCountLoading = false;
  //     state.fiveresp = res.dataDict.fiveresp;
  //     state.nineresp = res.dataDict.nineresp;
  //   });
  // };
  //分页页数的改变
  const pageNumberChange = (current, size) => {
    state.current = current;
    state.pageSize = size;
  };

  const respLineData = reactive({
    xList: [],
    dataList: [],
  });
  const statusLineData = reactive({
    xList: [],
    dataList: [],
  });
  const netLineData = reactive({
    xList: [],
    dataList: [],
  });
  const methodStLineData = reactive({
    xList: [],
    dataList: [],
  });
  const respPieData = reactive({});
  const statusPieData = reactive({});
  const methodPieData = reactive({});
  const clientPieData = reactive({});
  // import { getDataListByPage, createData, deleteData, updateData } from '@/api/log/apppass';
  const searchClick = (searchData) => {
    if (searchData?.isday) {
      state.isday = searchData?.isday;
    }
    trigHostTable(searchData);
    trigStatusLine(searchData);
    trigReqAllLine(searchData);
    trigNetAllLine(searchData);
    trigMethodStlLine(searchData);
    trigRespPie(searchData);
    trigStatusPie(searchData);
    trigMethodPie(searchData);
    trigClientPie(searchData);
  };
  onMounted(() => {});
</script>

<style lang="less" scoped>
  .screen {
    background: white;
    :deep(.ant-table-wrapper) {
      opacity: 0.8;
    }
    .digitshow {
      text-align: center;
      font-size: large;
      margin-top: 20px;
    }
    .block-box {
      width: 100%;
      padding: 1px;
      color: black;
      z-index: 10;
      border-bottom: 1px solid rgba(255, 255, 255, 0.4);
      border-left: 1px solid rgba(255, 255, 255, 0.4);
      background: linear-gradient(to top right, rgba(229, 233, 239, 0.5), rgba(212, 219, 229, 0.6));
      box-shadow: 1px;
      backdrop-filter: blur(6px); /*  元素后面区域添加模糊效果 */
      border-radius: 4px;
    }

    .gutter-row-3 {
      height: 400px;
    }
    .gutter-row-4 {
      height: 300px;
    }
    .gutter-row-5 {
      height: 600px;
    }
    .gutter-row-2 {
      height: 100px;
    }
    .gutter-row-1 {
      min-height: 80px;
    }
  }
</style>
