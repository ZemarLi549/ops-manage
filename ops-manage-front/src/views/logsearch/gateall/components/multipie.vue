<template>
  <div class="es-block">
    <div style="width: 100%; height: 90%">
      <Chart :option="option" />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, onMounted, watch } from 'vue';
  import Chart from '@/components/chart/Chart.vue';
  // const state = reactive({
  //   series: [],
  //   xList:[]
  // });

  const props = defineProps({
    id: {
      type: String,
      default() {
        return 'my_pie';
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
    series.value = newshowData.dataList;
  };

  onMounted(() => {
    computeInit(props.showData);
  });

  const option = reactive({
    title: {},
    tooltip: {
      trigger: 'item',
    },
    legend: {
      type: 'scroll',
      orient: 'vertical',
      left: '0',
    },
    toolbox: {
      show: true,
      feature: {
        mark: { show: true },
        dataView: { show: true, readOnly: false },
        magicType: { show: false },
        restore: { show: false },
        saveAsImage: { show: true },
      },
    },
    series: [
      {
        type: 'pie',
        radius: '50%',
        data: series,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
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
