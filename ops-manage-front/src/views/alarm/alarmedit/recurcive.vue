<template>
  <div>
    <Comment v-for="item in props.items" :key="item?.comment_time" :datetime="item?.comment_time">
      <template #actions>
        <span @click="replayStartFunc(item?.operator, item?.id)"> 回复 </span>
      </template>
      <template #author>
        <a>{{ item?.operator }}</a>
      </template>
      <template #avatar>
        <Avatar>{{ item?.operator }}</Avatar>
      </template>
      <template #content>
        <p v-html="item?.comment_content?.comment_text" />
      </template>
      <recursive-component
        v-if="item.children && item.children.length > 0"
        :items="item.children"
        @replyClick="replyClick"
      />
    </Comment>
  </div>
</template>

<script setup lang="ts">
  import { defineEmits } from 'vue';
  import { Avatar, Comment } from 'ant-design-vue';
  defineOptions({
    name: 'RecursiveComponent',
  });
  const props = defineProps({
    // 传进来的数据

    items: {
      type: Array,
      default: () => [],
    },
  });
  const replyClick = (replyData) => {
    emit('replyClick', replyData);
  };
  const emit = defineEmits(['replyClick']);
  const replayStartFunc = (operator, commentId) => {
    // console.log('operator, commentId', operator, commentId);
    emit('replyClick', { operator, commentId });
  };
</script>
<style lang="less" scoped>
  :deep(.ant-comment .ant-comment-content-detail) {
    font-size: 12px;
  }
</style>
