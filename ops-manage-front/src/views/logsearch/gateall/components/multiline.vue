<template>
  <div class="es-block">
    <div style="width: 100%; height: 100%">
      <Chart :option="option" />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, onMounted, watch } from 'vue';
  import * as echarts from 'echarts';
  import Chart from '@/components/chart/Chart.vue';
  // const state = reactive({
  //   series: [],
  //   xList:[]
  // });

  const props = defineProps({
    id: {
      type: String,
      default() {
        return 'my_line';
      },
    },
    // 传进来的数据
    showData: {
      type: Object,
      default() {
        return { xList: [], dataList: [] };
      },
    },
  });
  const xList = ref([]);
  const series = ref([]);

  watch(
    props.showData,
    (newShowData: any) => {
      computeInit(newShowData);
    },
    { deep: true }, //很重要
  );
  // watch(
  //   () => shallowReactive(props.showData),
  //   (newValue, oldValue) => {
  //     console.log('prop data cahge>>>>', newValue);
  //     computeInit(newValue);
  //   },
  // );
  const computeInit = (newshowData) => {
    xList.value = newshowData.xList;
    series.value = [];
    newshowData.dataList.map((item) => {
      const seriesDict = {
        name: item.name,
        type: 'line',
        smooth: true,
        data: item.yList,
        symbol: 'none',
        markPoint: {
          data: [{ type: 'max', name: '最大值', symbolSize: [80, 40] }],
        },
      };
      series.value.push(seriesDict);
    });
  };

  onMounted(() => {
    computeInit(props.showData);
  });

  const option = reactive({
    title: {},
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
      },
      confine: true,
      formatter(params) {
        let newParams = [];
        const tooltipString = [`${params[0].name}<br/>`];
        newParams = [...params];
        newParams.sort((a, b) => {
          return b.value - a.value;
        });
        newParams.forEach((p) => {
          const cont = `${p.marker} ${p.seriesName}: ${p.value}<br/>`;
          tooltipString.push(cont);
        });
        return tooltipString.join('');
      },
    },
    dataZoom: [
      {
        type: 'inside',
      },
    ],
    legend: {
      type: 'scroll',
      icon: 'roundRect',
      // formatter(name) {
      //   return echarts.format.truncateText(name, 50, '14px Microsoft Yahei', '…');
      // },
      tooltip: {
        show: true,
      },
    },
    grid: {
      left: '10%',
      right: '4%',
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: xList,
    },
    yAxis: {
      type: 'value',
      // axisLabel: {
      //   formatter: '{value}',
      // },
    },
    series,
  });
</script>

<style lang="scss" scoped>
  .es-block {
    width: 100%;
    height: 100%;
  }
</style>
