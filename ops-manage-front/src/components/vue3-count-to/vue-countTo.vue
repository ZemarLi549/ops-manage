<template>
  <BaseCountTo
    ref="vueCountTo"
    :start-val="startVal"
    :end-val="endVal"
    :duration="duration"
    :decimals="decimals"
    :prefix="prefix"
    :suffix="suffix"
    :decimal="decimal"
    :separator="separator"
  />
</template>

<script lang="ts">
  import { defineComponent, toRefs, ref, onMounted, unref, onBeforeUnmount, watch } from 'vue';
  import { CountTo as BaseCountTo } from 'vue3-count-to';

  import type { PropType } from 'vue';

  export default defineComponent({
    name: 'CountTo',

    components: { BaseCountTo },

    props: {
      duration: {
        type: Number as PropType<number>,

        default: 3000,
      },

      startVal: {
        type: Number as PropType<number>,

        default: 0,
      },

      endVal: {
        type: Number as PropType<number>,

        default: 0,
      },

      enableLoop: {
        //是否开启循环

        type: Boolean as PropType<boolean>,

        default: false,
      },

      loopTime: {
        //循环事件

        type: Number as PropType<number>,

        default: 10 * 1000,
      },

      decimals: {
        //小数点位数

        type: Number as PropType<number>,

        default: 0,
      },

      prefix: {
        //前缀

        type: String as PropType<string>,

        default: '',
      },

      suffix: {
        //后缀

        type: String as PropType<string>,

        default: '',
      },

      decimal: {
        //十进制分割

        type: String as PropType<string>,

        default: '.',
      },

      separator: {
        //分隔符

        type: String as PropType<string>,

        default: ',',
      },
    },

    setup(props) {
      const vueCountTo = ref<null | HTMLElement>(null);

      let timer: any = null;

      onMounted(() => {
        addLoop();
      });

      //添加循环

      const addLoop = () => {
        if (props.enableLoop) {
          const dom = unref(vueCountTo);

          if (dom) {
            // console.log(dom)

            timer = setInterval(() => {
              (dom as any).reset();
              (dom as any).start();
            }, props.loopTime as number);
          }
        }
      };

      watch(
        () => props.endVal,

        () => {
          clearInterval(timer);

          addLoop();
        },
      );

      onBeforeUnmount(() => {
        clearInterval(timer);
      });

      return {
        ...toRefs(props),

        vueCountTo,
      };
    },
  });
</script>

<style lang="scss" scoped></style>
