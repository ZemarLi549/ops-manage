<template>
  <h3 class="es-screen-title">
    <slot>
      {{ title }}
    </slot>
  </h3>
</template>

<script setup lang="ts">
  defineProps({
    title: String,
  });
</script>

<style lang="scss" scoped>
  .es-screen-title {
    position: relative;
    padding-left: 20px;
    &::before {
      content: '';
      position: absolute;
      left: 8px;
      top: 0;
      width: 3px;
      height: 100%;
      background-color: black;
    }
  }
</style>
