<template>
  <div ref="chartRef" className="es-chart"></div>
</template>

<script setup lang="ts">
  import 'echarts/theme/macarons2.js';
  import { onMounted, PropType, shallowRef, watch, onUnmounted, ref } from 'vue';
  import * as echarts from 'echarts';
  import { ECharts, EChartsCoreOption } from 'echarts';

  const props = defineProps({
    option: {
      type: Object as PropType<EChartsCoreOption>,
      default: () => ({}),
    },
    loading: Boolean,
  });
  const chartRef = shallowRef<HTMLElement | null>(null);
  const timeout = ref(null);
  const chart = shallowRef<ECharts | null>(null);
  function init() {
    if (props.option) {
      setTimeout(() => {
        chart.value = echarts.init(chartRef.value!, 'macarons2');
        chart.value.resize();
        setOption(props.option);
      }, 1000);
    }
  }
  function setOption(option, notMerge?: boolean, lazyUpdate?: boolean) {
    if (option) {
      chart.value!.setOption(option, notMerge, lazyUpdate);
    }
  }

  function resize() {
    chart.value!.resize();
  }

  watch(
    () => props.option,
    (newOption) => {
      setTimeout(() => {
        setOption(newOption);
      });
    },
    { deep: true }, //很重要
  );

  // show loading
  watch(
    () => props.loading,
    (val) => {
      if (!chart.value) return;
      if (val) {
        chart.value!.showLoading();
      } else {
        chart.value!.hideLoading();
      }
    },
    // { deep: true },
  );
  // const chartDivRef = ref(null);
  const resizeObserver = new ResizeObserver((entries) => {
    if (timeout.value) {
      clearTimeout(timeout.value);
    }
    // 设置新的定时器
    timeout.value = setTimeout(() => {
      // console.log(entries[0].contentRect.width);
      // console.log(entries[0].contentRect.height);
      init();
    }, 200); // 延迟100毫秒执行
  });
  onMounted(() => {
    // init();

    resizeObserver.observe(chartRef.value);
  });
  onUnmounted(() => {
    resizeObserver.unobserve(chartRef.value);
  });

  defineExpose({
    chart,
    setOption,
    resize,
  });
</script>

<style lang="scss" scoped>
  .es-chart {
    width: 100%;
    height: 100%;
  }
</style>
