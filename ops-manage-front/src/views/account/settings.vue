<template>
  <div> 个人中心 </div>
  <a-button type="link" @click="openUpdatePasswordModal">改密</a-button>
</template>
<script setup lang="tsx">
  import { computed } from 'vue';
  import { updatePswSchemas } from './formSchemas';
  import { useUserStore } from '@/store/modules/user';
  import { updateUserPassword } from '@/api/system/user';
  import { useFormModal } from '@/hooks/useModal/index';
  const [showModal] = useFormModal();
  const userStore = useUserStore();
  const userInfo = computed(() => userStore.userInfo);
  defineOptions({
    name: 'UserInfo',
  });

  /**
   * 打开更新用户密码弹窗
   */
  const openUpdatePasswordModal = async () => {
    const name = userInfo.value.name;
    await showModal({
      modalProps: {
        title: `修改密码(${name})`,
        width: 700,
        onFinish: async (values) => {
          await updateUserPassword({
            name,
            password: values.password,
          });
        },
      },
      formProps: {
        labelWidth: 100,
        schemas: updatePswSchemas,
      },
    });
  };
</script>
