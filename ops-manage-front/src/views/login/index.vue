<template>
  <div class="login-box">
    <div class="login-logo">
      <h1 class="mb-0 ml-2 text-3xl font-bold">运维平台</h1>
    </div>
    <div>
      <a-form layout="horizontal" :model="state.formInline" @submit.prevent="handleSubmit">
        <a-form-item>
          <a-input v-model:value="state.formInline.username" size="large" placeholder="admin">
            <template #prefix><user-outlined type="user" /></template>
          </a-input>
        </a-form-item>
        <a-form-item>
          <a-input
            v-model:value="state.formInline.password"
            size="large"
            type="password"
            placeholder="123456"
            autocomplete="new-password"
          >
            <template #prefix><lock-outlined type="user" /></template>
          </a-input>
        </a-form-item>
        <!-- <a-form-item>
        <a-input
          v-model:value="state.formInline.verifyCode"
          placeholder="验证码"
          :maxlength="4"
          size="large"
        >
          <template #prefix><SafetyOutlined /></template>
          <template #suffix>
            <img
              :src="state.captcha"
              class="absolute right-0 h-full cursor-pointer"
              @click="setCaptcha"
            />
          </template>
        </a-input>
      </a-form-item> -->
        <a-form-item>
          <a-button type="primary" html-type="submit" size="middium" :loading="state.loading" block>
            登录
          </a-button>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" size="middium" block @click="loginWithIbase">
            集团账号登录
          </a-button>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" size="middium" block @click="regFunc"> 注册 </a-button>
        </a-form-item>
      </a-form>
    </div>
    <a-modal
      v-model:visible="state.credModalVisible"
      title="注册用户"
      cancel-text="取消"
      ok-text="确定"
      :keyboard="false"
      :mask-closable="false"
      @ok="onSubmit"
    >
      <a-form
        ref="formRef"
        :model="state.formState"
        :rules="rules"
        :label-col="state.labelCol"
        :wrapper-col="state.wrapperCol"
      >
        <a-form-item label="用户名" name="regUser">
          <a-input v-model:value="state.formState.regUser" allow-clear placeholder="请输入用户名" />
        </a-form-item>
        <a-form-item label="密码" name="regPwd">
          <a-input
            v-model:value="state.formState.regPwd"
            type="password"
            allow-clear
            placeholder="请输入密码"
          />
        </a-form-item>
        <a-form-item label="中文名" name="realname">
          <a-input
            v-model:value="state.formState.realname"
            allow-clear
            placeholder="请输入中文名"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
  import { reactive, ref, onMounted, onBeforeMount } from 'vue';
  import { UserOutlined, LockOutlined, SafetyOutlined } from '@ant-design/icons-vue';
  import { useRoute, useRouter } from 'vue-router';
  import { message, Modal } from 'ant-design-vue';
  import { useUserStore } from '@/store/modules/user';
  import { getImageCaptcha, regNewUser } from '@/api/login';
  import { to } from '@/utils/awaitTo';
  import { Storage } from '@/utils/Storage';
  onMounted(() => {
    console.log('nounted.>>>');
  });
  const state = reactive({
    labelCol: {
      span: 4,
    },
    wrapperCol: {
      span: 19,
    },
    formState: {
      regUser: '',
      regPwd: '',
      realname: '',
    },
    credModalVisible: false,
    loading: false,
    captcha: '',
    formInline: {
      username: '',
      password: '',
      verifyCode: '',
      captchaId: '',
    },
  });
  const formRef = ref();
  const route = useRoute();
  const router = useRouter();

  const userStore = useUserStore();
  const rules = {
    regUser: [
      {
        required: true,
        min: 3,
        max: 25,
        message: '名称长度应为3~25',
        trigger: 'blur',
      },
    ],
    regPwd: [
      {
        required: true,
        min: 6,
        max: 25,
        message: '密码长度应为6~25',
        trigger: 'blur',
      },
    ],
  };
  const loginWithIbase = () => {
    setTimeout(() => {
      // console.log('process.env.VUE_APP_SSO_LOGIN', process.env.VUE_APP_SSO_LOGIN);
      window.location.href = `${process.env.VUE_APP_SSO_LOGIN}#/login?redirect=${
        (route.query.redirect as string) ?? '/'
      }`;
      // window.location.href = `https://ssoqxb.iflytek.com:8443/sso/login?service=http://127.0.0.1:8098/#/login`;
    });
  };
  const onSubmit = () => {
    formRef.value.validate().then(() => {
      const params = Object.fromEntries(Object.entries(state.formState));

      regNewUser(params).finally(() => {
        state.credModalVisible = false;
        formRef.value.resetFields();
      });
    });
  };
  const setCaptcha = async () => {
    const { id, img } = await getImageCaptcha({ width: 50, height: 50 });
    state.captcha = img;
    state.formInline.captchaId = id;
  };
  // setCaptcha();
  const regFunc = () => {
    state.credModalVisible = true;
  };
  onBeforeMount(async () => {
    const currentUrl = window.location.href;
    const url = new URL(currentUrl);

    // 获取 URL 中的查询参数
    const searchParams = new URLSearchParams(url.search);

    // 获取 ticket 参数的值
    const ticketValue = searchParams.get('ticket');
    // console.log('currentUrl>>>', currentUrl);
    // const result = `${url.protocol}//${url.host}/#${(route.query.redirect as string) ?? '/'}`;
    // console.log('result>>>', result);
    // 检查 ticket 是否存在
    if (ticketValue) {
      // console.log('Ticket 存在:', ticketValue);
      Storage.set('ssoTicket', ticketValue, 7 * 24 * 60 * 60);
      message.loading('登录中...', 0);
      state.loading = true;
      const [err] = await to(userStore.login({ ticket: ticketValue }));
      if (err) {
        Modal.error({
          title: () => '提示',
          content: () => err.message,
        });
        setCaptcha();
      } else {
        message.success('登录成功！');
        setTimeout(() => {
          const result = `${url.protocol}//${url.host}/#${(route.query.redirect as string) ?? '/'}`;
          window.location.href = result;
        });
      }
      state.loading = false;
      message.destroy();
    } else {
      console.log('Ticket 不存在', route.query.redirect);
    }
  });
  const handleSubmit = async () => {
    const { username, password, verifyCode } = state.formInline;
    if (username.trim() == '' || password.trim() == '') {
      return message.warning('用户名或密码不能为空！');
    }
    // if (!verifyCode) {
    //   return message.warning('请输入验证码！');
    // }
    message.loading('登录中...', 0);
    state.loading = true;
    console.log(state.formInline);
    // params.password = md5(password)

    const [err] = await to(userStore.login(state.formInline));
    if (err) {
      Modal.error({
        title: () => '提示',
        content: () => err.message,
      });
      setCaptcha();
    } else {
      message.success('登录成功！');
      setTimeout(() => router.replace((route.query.redirect as string) ?? '/'));
    }
    state.loading = false;
    message.destroy();
  };
</script>

<style lang="less" scoped>
  .login-box {
    display: flex;
    width: 100vw;
    height: 100vh;
    padding-top: 240px;
    background: url('~@/assets/login.svg');
    background-size: 100%;
    flex-direction: column;
    align-items: center;
    overflow-y: scroll;

    .login-logo {
      display: flex;
      margin-bottom: 30px;
      align-items: center;

      .svg-icon {
        font-size: 48px;
      }
    }

    :deep(.ant-form) {
      width: 40%;
      min-width: 340px;

      .ant-col {
        width: 100%;
      }

      .ant-form-item-label {
        padding-right: 6px;
      }
    }
  }
</style>
