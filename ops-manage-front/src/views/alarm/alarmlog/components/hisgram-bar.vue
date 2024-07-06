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

  const props = defineProps({
    id: {
      type: String,
      default() {
        return 'my_bar';
      },
    },
    // 传进来的数据
    showData: {
      type: Object,
      default() {
        return { dataList: [] };
      },
    },
  });
  const series = ref([]);
  const xList = ref([]);
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
    series.value = [];
    xList.value = [];
    newshowData.dataList.map((item) => {
      xList.value.push(item.name);
      series.value.push(item.value);
    });
    series.value = newshowData.dataList;
  };

  onMounted(() => {
    computeInit(props.showData);
  });

  const option = reactive({
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
        label: {
          show: true,
        },
      },
    },
    toolbox: {
      show: true,
      feature: {
        mark: { show: true },
        dataView: { show: true, readOnly: false },
        magicType: { show: true, type: ['line', 'bar'] },
        saveAsImage: { show: true },
      },
    },
    calculable: true,
    legend: {
      data: ['count', 'date'],
      itemGap: 5,
    },
    // grid: {
    //   top: '12%',
    //   left: '1%',
    //   right: '10%',
    //   containLabel: true,
    // },
    xAxis: [
      {
        type: 'category',
        data: xList,
      },
    ],
    yAxis: [
      {
        type: 'value',
        name: 'count (条)',
        axisLabel: {
          formatter(a) {
            a = +a;
            return isFinite(a) ? echarts.format.addCommas(+a) : '';
          },
        },
      },
    ],
    dataZoom: [
      {
        type: 'inside',
      },
    ],
    series: [
      {
        name: 'series',
        type: 'bar',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' },
          ]),
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#2378f7' },
              { offset: 0.7, color: '#2378f7' },
              { offset: 1, color: '#83bff6' },
            ]),
          },
        },
        barMaxWidth: '40%',
        data: series,
      },
    ],
  });
</script>

<style lang="scss" scoped>
  .es-block {
    width: 100%;
    height: 100%;
  }
</style>
