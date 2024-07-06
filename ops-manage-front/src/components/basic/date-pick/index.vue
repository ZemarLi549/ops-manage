<template>
  <a-date-picker v-model:value="selectedDate" :format="dateFormat" />
</template>

<script>
  import { ref, watch } from 'vue';
  import { DatePicker } from 'ant-design-vue';

  export default {
    components: {
      ADatePicker: DatePicker,
    },
    props: {
      value: {
        type: String,
        default: '',
      },
    },
    setup(props, { emit }) {
      const selectedDate = ref(props.value);
      const dateFormat = 'YYYY-MM-DD';

      watch(selectedDate, (newVal) => {
        emit('update:value', newVal);
      });

      return {
        selectedDate,
        dateFormat,
      };
    },
  };
</script>
