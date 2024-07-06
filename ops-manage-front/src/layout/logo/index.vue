<template>
  <div class="logo">
    <span class="title">运维平台</span>
  </div>
</template>

<script setup>
  defineProps({
    collapsed: {
      type: Boolean,
    },
  });
</script>

<style lang="less" scoped>
  .logo {
    @apply flex overflow-hidden whitespace-nowrap items-center;

    height: 64px;
    padding-left: 4px;
    line-height: 64px;

    img {
      height: 32px;
      margin-right: 0px;
    }

    .title {
      font-size: 14px;
      // @apply mb-0 text-xl;
      color: @primary-color;
    }
  }
</style>
