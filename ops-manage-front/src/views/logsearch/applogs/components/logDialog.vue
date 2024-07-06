<template>
  <a-spin :spinning="state.pullLoading">
    <div class="wrapper">
      <div class="content">
        <p
          v-for="(goodsOne, index) in state.logDataList"
          :key="index"
          class="log-text"
          :style="activation(goodsOne?.content)"
          v-html="goodsOne?.content"
        >
        </p>
      </div>
    </div>
  </a-spin>
</template>

<script setup lang="ts">
  import { onMounted, reactive, nextTick, computed } from 'vue';
  import BScroll from 'better-scroll';
  import { appLocate } from '@/api/log/app';

  //引入better-scroll
  //改变日志颜色 :style="activation(content)"
  const activation = computed(() => {
    return (content) => {
      const lowerContent = content.toLowerCase();
      if (lowerContent.includes('info'.toLowerCase())) {
        return { color: '#D3D3D3' };
      } else if (lowerContent.includes('error'.toLowerCase())) {
        return { color: '#ff0808' };
      } else if (lowerContent.includes('warn'.toLowerCase())) {
        return { color: '#FFA500' };
      } else if (lowerContent.includes('debug'.toLowerCase())) {
        return { color: '#008000' };
      } else if (lowerContent.includes('critical'.toLowerCase())) {
        return { color: '#8B0000' };
      } else {
        return { color: '#D3D3D3' };
      }
    };
  });
  const props = defineProps({
    localSearchData: {
      type: Object,
      default() {
        return {};
      },
    },
    locateType: {
      type: String,
      default() {
        return 'normal';
      },
    },
    // 传进来的数据
    record: {
      type: Object,
      default() {
        return {};
      },
    },
  });
  // watch(
  //   props.record,
  //   (newShowData: any) => {
  //     initLocate(newShowData);
  //   },
  //   { deep: true }, //很重要
  // );
  const state = reactive({ pullLoading: false, logDataList: [], stopPoint: 0 });

  let bscroll = reactive({});
  onMounted(() => {
    setTimeout(() => {
      bscroll = new BScroll(document.querySelector('.wrapper'), {
        scrollY: true,
        observeDOM: true,
        startY: 0,
        preventDefault: false,
        probeType: 3,
        click: false,
        bounce: {
          top: true,
          bottom: true,
        },
        scrollbar: {
          fade: false,
        },
        //pullUpLoad:true,
        pullUpLoad: {
          // 当上拉距离超过10px时触发 pullingUp 事件
          threshold: -40,
          // stop: 100,
        },
        mouseWheel: true,
        pullDownRefresh: {
          // stop: 100,
          threshold: 40,
        },
      });
      bscroll.on('pullingUp', async () => {
        console.log('现在正在下拉加载更多...');
        if (state.logDataList.length > 10000) {
          state.logDataList = state.logDataList.slice(110);
        }
        state.pullLoading = true;
        await scrollFun('next'); //请求数据
        state.pullLoading = false;
        bscroll.finishPullUp(); //上拉加载动作结束,
        bscroll.refresh(); //重新计算 BetterScroll
      });
      bscroll.on('pullingDown', async () => {
        console.log('处理上拉刷新操作');
        //防止dom过多
        if (state.logDataList.length > 10000) {
          state.logDataList = state.logDataList.slice(0, state.logDataList.length - 110);
        }
        state.pullLoading = true;
        await scrollFun('prev'); //请求数据
        state.pullLoading = false;
        bscroll.finishPullDown(); //下拉加载动作结束
        bscroll.refresh(); //重新计算 BetterScroll
      });
    });
    initLocate();
  });
  //保存页面数据的数组
  const initLocate = async () => {
    console.log('props>>>', props);
    const requestData = Object.assign({}, props.localSearchData, {
      scrollType: 'both',
      locateType: props.locateType,
      search_after: props.record.search_after,
    });
    state.logDataList = [];
    state.pullLoading = true;
    await appLocate(requestData).then((res) => {
      state.pullLoading = false;
      if (res.data?.prev) {
        state.logDataList.unshift(...res.data.prev);
        state.stopPoint = res.data.prev.length + 1;
      }

      const separation =
        '---------------------------------------------定位此处---------------------------------------------';
      state.logDataList.push({
        content: `${separation}\n[${props.record.message.time_str}]  ${props.record.message.message}`,
        search_after: props.record.search_after,
      });
      if (res.data?.next) {
        state.logDataList.push(...res.data.next);
      }
    });
    await nextTick();
    const pEle = document.querySelector(`.content p:nth-child(${state.stopPoint})`);
    bscroll.scrollToElement(pEle, 100);
  };
  const scrollFun = async (pullType) => {
    const requestData = Object.assign({}, props.localSearchData, {
      scrollType: pullType,
      locateType: props.locateType,
    });
    if (pullType == 'next') {
      requestData.search_after = state.logDataList.slice(-1)[0].search_after;
    } else if (pullType == 'prev') {
      requestData.search_after = state.logDataList[0].search_after;
    }

    await appLocate(requestData).then((res) => {
      if (res.data?.prev) {
        state.logDataList.unshift(...res.data.prev);
        state.stopPoint = res.data.prev.length + 1;
      }
      if (res.data?.next) {
        state.logDataList.push(...res.data.next);
        state.stopPoint = state.logDataList.length - res.data.next.length;
      }
    });
    await nextTick();
    const pEle = document.querySelector(`.content p:nth-child(${state.stopPoint})`);
    bscroll.scrollToElement(pEle, 100);
  };
</script>

<style scoped>
  .wrapper {
    overflow-y: hidden;
    width: 100%;
    height: 80vh;
    background: #0a0a09;
    color: aliceblue;
    border: 6px solid white;
    padding: 4px;
  }
  .log-text {
    white-space: pre-wrap;
    width: 100%;
    line-height: 24px;
    font-size: 14px;
  }
  .warn {
    color: rgb(226, 226, 115) !important;
  }
  /* .content {
    height: 1000px;
  } */
</style>
