<template>
  <div>
    <a-spin :spinning="state.commentLoading">
      <div>
        <Divider orientation="left" :plain="true"> {{ state.commentCount }}个评论 </Divider>

        <RecursiveComponent :items="state.commentList" />
      </div>
    </a-spin>
  </div>
</template>
<script setup lang="ts">
  import { onMounted, reactive } from 'vue';
  import { Divider } from 'ant-design-vue';
  import RecursiveComponent from './recurcive.vue';
  import { getDataListByPage } from '@/api/alarm/comment';
  const props = defineProps({
    // 传进来的数据
    identityId: {
      type: Number,
      default() {
        return 1;
      },
    },
  });

  const state = reactive({
    commentLoading: false,
    commentList: [],
    commentCount: 0,
    login_user: '',
    commentPlaceholder: '评论...',
  });

  // 获取信息
  const getDataList = async () => {
    const params = {
      identity_id: props.identityId,
    };
    state.commentLoading = true;
    await getDataListByPage(params).then((res) => {
      state.commentLoading = false;
      state.commentList = res.data;
      state.commentCount = res.count;
      state.login_user = res.login_user;
    });

    // state.size = data.size
  };

  defineOptions({
    name: 'Comment',
  });
  onMounted(() => {
    getDataList();
  });
</script>

<style lang="less" scoped></style>
