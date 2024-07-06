<template>
  <div>
    <a-spin :spinning="state.commentLoading">
      <div>
        <Divider orientation="left" :plain="true"> {{ state.commentCount }}个评论 </Divider>

        <RecursiveComponent :items="state.commentList" @replyClick="replyClick" />
        <Comment>
          <template #content>
            <a-form
              ref="formRef"
              :model="commentFormState"
              :label-col="{ span: 0 }"
              :wrapper-col="{ span: 22 }"
            >
              <a-form-item label="" name="comment_text">
                <a-textarea
                  v-model:value="commentFormState.comment_text"
                  :placeholder="state.commentPlaceholder"
                  :rows="4"
                />
              </a-form-item>
              <a-form-item>
                <a-button type="primary" @click="onStatusSubmit">添加评论</a-button>
              </a-form-item>
            </a-form>
          </template>
          <template #avatar>
            <Avatar>{{ state.login_user }}</Avatar>
          </template>
        </Comment>
      </div>
    </a-spin>
  </div>
</template>
<script setup lang="ts">
  import { onMounted, reactive, ref } from 'vue';
  import { Divider, Avatar, Comment } from 'ant-design-vue';
  import RecursiveComponent from './recurcive.vue';
  import { putDataListByPage, createData } from '@/api/alarm/comment';
  const props = defineProps({
    // 传进来的数据
    identityId: {
      type: Number,
      default() {
        return 1;
      },
    },
  });
  const formRef = ref();

  const commentFormState = reactive({
    comment_type: 'text',
    identity_id: props.identityId,
    pre_comment: 0,
    comment_text: '',
  });
  const state = reactive({
    commentLoading: false,
    commentList: [],
    commentCount: 0,
    login_user: '',
    commentPlaceholder: '评论...',
  });
  const replyClick = (replyData) => {
    state.commentPlaceholder = ` 回复 <${replyData.operator}>`;
    commentFormState.pre_comment = replyData.commentId;
  };
  const onStatusSubmit = () => {
    const params = Object.fromEntries(Object.entries(commentFormState));
    createData(params).then((res) => {
      if (res.status && res.status == 'success') {
        state.commentPlaceholder = '评论...';
        commentFormState.pre_comment = 0;
        commentFormState.comment_text = '';
        getDataList();
      }
    });
  };
  // 获取信息
  const getDataList = async () => {
    const params = {
      identity_id: props.identityId,
    };
    state.commentLoading = true;
    await putDataListByPage(params).then((res) => {
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
