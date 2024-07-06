import dayjs from 'dayjs';

export const dateRange = () => {
  const dateChoose = {
    近15分钟: [dayjs().subtract(15, 'm'), dayjs()],
    近30分钟: [dayjs().subtract(30, 'm'), dayjs()],
    近1小时: [dayjs().subtract(1, 'h'), dayjs()],
    近2小时: [dayjs().subtract(2, 'h'), dayjs()],
    近4小时: [dayjs().subtract(4, 'h'), dayjs()],
    近8小时: [dayjs().subtract(8, 'h'), dayjs()],
    昨天: [dayjs().subtract(1, 'day').startOf('day'), dayjs().subtract(1, 'day').endOf('day')],
    上周: [dayjs().subtract(7, 'day').startOf('week'), dayjs().subtract(7, 'day').endOf('week')],
  };
  return dateChoose;
};
