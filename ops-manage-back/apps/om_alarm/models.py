from django.db import models
from django.utils.timezone import now
from django.db.backends.mysql.base import DatabaseWrapper

DatabaseWrapper.data_types['DateTimeField'] = 'datetime'


# Create your models here.

class CustomQuerySetManager(models.Manager):
    """A re-usable Manager to access a custom QuerySet"""

    # _queryset_class = SoftDeletableQuerySet

    def __init__(self, *args, **kwargs):
        super(CustomQuerySetManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        """
        在这里处理一下QuerySet, 然后返回没被标记位delete_mark的QuerySet
        """
        kwargs = {'model': self.model, 'using': self._db}
        if hasattr(self, '_hints'):
            kwargs['hints'] = self._hints
        return self._queryset_class(**kwargs).filter(delete_mark='1')


# bettle要求字段,基类
class BaseModel(models.Model):
    id = models.AutoField(
        db_column='id', help_text='主键ID', primary_key=True)

    created_at = models.DateTimeField(
        db_column='created_at', help_text='创建时间', auto_now_add=True)
    created_by = models.CharField(
        default="sys", db_column='created_by', help_text='创建者', max_length=32, null=True)
    updated_at = models.DateTimeField(
        db_column='updated_at', help_text='更新时间', auto_now=True)
    updated_by = models.CharField(
        default="sys", db_column='updated_by', help_text='更新者', max_length=32, null=True)

    class Meta:
        abstract = True

    # 每次查询都需要添加delete_mark=1
    # objects = CustomQuerySetManager()

    @property
    def properties(self):
        return list(map(lambda _d: _d.name, filter(
            lambda _d: lambda _d: not _d.primary_key and not isinstance(_d.formfield.__self__, models.DateTimeField),
            self._meta.fields)))

    # 获取所有字段，除开datetime类型
    def columns(self):
        return list(map(lambda _d: _d.column, filter(
            lambda _d: lambda _d: not _d.primary_key and not isinstance(_d.formfield.__self__, models.DateTimeField),
            self._meta.fields)))

    # 将对象作为字典数据，除开datetime类型，如果要添加datetime类型在CustomJSONEncoder中添加
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in filter(
            lambda _d: not isinstance(_d.formfield.__self__, models.DateTimeField), self._meta.fields)}

    # 将对象作为字典数据，如果要添加datetime类型在CustomJSONEncoder中添加
    def pure_as_dict(self):
        return {c.name: getattr(self, c.name) for c in self._meta.fields}


class AlarmUser(BaseModel):
    name = models.CharField(help_text='中文名称', max_length=32, null=True, blank=True)
    username = models.CharField(max_length=32, unique=True, db_index=True)
    phone = models.CharField(max_length=24, null=True, blank=True)
    email = models.CharField(max_length=32, null=True, blank=True)
    desc = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        managed = True
        db_table = 'alarm_user'


class AlarmConfig(models.Model):
    id = models.IntegerField(db_column='id', help_text='主键ID', primary_key=True)
    created_at = models.DateTimeField(
        db_column='created_at', help_text='创建时间', default=now, null=True)
    created_by = models.CharField(
        default="sys", db_column='created_by', help_text='创建者', max_length=32, null=True)
    updated_at = models.DateTimeField(
        db_column='updated_at', help_text='更新时间', auto_now=True)
    updated_by = models.CharField(
        default="sys", db_column='updated_by', help_text='更新者', max_length=32, null=True)
    name = models.CharField(help_text='名称', max_length=32, null=True, blank=True)
    alarm_to = models.JSONField(default={'wechat': [], 'sms': [], 'phone': [], 'ding': [], 'email': []}, null=True,
                                blank=True)
    rule_name = models.CharField(help_text='AlarmRule名称', max_length=32, null=True, blank=True, db_index=True)
    alert_start = models.CharField(help_text='一天内告警开始时间08:00', max_length=8, null=True, blank=True)
    alert_end = models.CharField(help_text='一天内告警结束时间21:00', max_length=8, null=True, blank=True)
    desc = models.CharField(max_length=64, null=True, blank=True)
    send_type = models.CharField(default="common", db_column='send_type', help_text='发送规则', max_length=16)
    label_name = models.CharField(default="source", db_column='label_name', help_text='分类lable', max_length=16)
    #{"森华集群":{'wechat': [], 'sms': [], 'phone': [], 'ding': [], 'email': []}}
    label_send = models.JSONField(default=[], null=True,blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        managed = True
        db_table = 'alarm_config'


class AlarmRule(BaseModel):
    name = models.CharField(max_length=32, unique=True, db_index=True)
    rule_keys = models.CharField(help_text='组成指纹的几个key', max_length=64, blank=True)
    rule_re = models.CharField(help_text='从告警内容取key加入指纹', max_length=64, blank=True)
    rate = models.IntegerField(help_text='基础评分', default=1)
    freq = models.CharField(help_text='告警频率', max_length=32, null=True, blank=True)
    resovle_freq = models.CharField(help_text='恢复告警频率', max_length=32, null=True, blank=True)
    desc = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        managed = True
        db_table = 'alarm_rule'


class AlarmBlack(BaseModel):
    name = models.CharField(max_length=32, unique=True, db_index=True)
    rule_re = models.CharField(help_text='从summary中取出', max_length=64, blank=True)
    black_to = models.DateTimeField(help_text='截至时间', blank=True, null=True)
    desc = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        managed = True
        db_table = 'alarm_black'


class CacheRead(BaseModel):
    datatype = models.CharField(db_column='datatype', help_text='datatype', max_length=128, null=True)
    cachestr = models.TextField(db_column='cachestr', help_text='cachestr', null=True, blank=True)
    note = models.CharField(db_column='note', help_text='note', max_length=128, null=True, blank=True)

    def __str__(self):
        return str(self.datatype)

    class Meta:
        verbose_name_plural = verbose_name = 'cache'
        managed = True
        db_table = 'alarm_cacheread'


class AlarmIdentity(models.Model):
    "指纹记录表"

    class Status(models.TextChoices):
        # 消除就放到历史中就不收敛了
        DISARBLE = (0, "消除")
        PROCESSING = (1, "正在处理")
        COMPLETED = (2, "处理完成")
        IGNORE = (3, "暂时忽略")
        UNDISPOSED = (4, "未处理")
        AUTOECOVER = (5, "自动恢复")

        @classmethod
        def select(cls, label):
            Choices_name = 0
            for i in cls.__members__.values():
                if i.label == label:
                    Choices_name = i
                    break
            return Choices_name

    id = models.AutoField(db_column='id', help_text='主键ID', primary_key=True, default=1000)
    identity = models.CharField(max_length=250, blank=True, null=True, db_index=True)
    identity_tag_kv = models.JSONField(blank=True, null=True, default=dict)
    times = models.IntegerField(blank=True, null=True)
    recover_cnt = models.IntegerField(blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(choices=Status.choices,
                                 default=Status.UNDISPOSED,
                                 help_text="状态")
    created_at = models.DateTimeField(
        db_column='created_at', help_text='创建时间', auto_now_add=True)
    created_by = models.CharField(
        default="sys", db_column='created_by', help_text='创建者', max_length=32, null=True)
    updated_at = models.DateTimeField(
        db_column='updated_at', help_text='更新时间', auto_now=True)
    updated_by = models.CharField(
        default="sys", db_column='updated_by', help_text='更新者', max_length=32, null=True)

    ignore_to = models.DateTimeField(help_text='忽略截至时间', blank=True, null=True)
    record_ignore = models.BooleanField(default=True, help_text='忽略时候是否记录数据到es')
    handler = models.CharField(max_length=250,
                               blank=True,
                               null=True,
                               help_text="处理人")

    class Meta:
        managed = True
        db_table = 'alarm_identity'


# class AlarmSolution(BaseModel):
#     reach = models.CharField(max_length=1500, blank=True, null=True)
#     reason = models.CharField(max_length=1500, blank=True, null=True)
#     solution = models.CharField(max_length=1500, blank=True, null=True)
#     identity = models.ForeignKey(to=AlarmIdentity, on_delete=models.CASCADE, related_name="alarm_solution",
#                                  verbose_name='指纹', default=1)
#
#     def __str__(self):
#         return str(self.id)
#
#     class Meta:
#         managed = False
#         db_table = 'alarm_solution'


class AlarmZongjie(BaseModel):
    reach = models.CharField(max_length=1500, blank=True, null=True)
    reason = models.CharField(max_length=1500, blank=True, null=True)
    solution = models.CharField(max_length=1500, blank=True, null=True)
    # identity = models.ForeignKey(to=AlarmIdentity, on_delete=models.CASCADE, related_name="alarm_zongjie",
    #                              verbose_name='指纹', default=1)
    identity_id = models.IntegerField(help_text='指纹ID', db_index=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        managed = True
        db_table = 'alarm_zongjie'


class AlarmComment(BaseModel):
    identity = models.ForeignKey(to=AlarmIdentity, on_delete=models.CASCADE, related_name="alarm_comment",
                                 verbose_name='指纹')
    comment_content = models.JSONField(verbose_name='评论内容')
    comment_time = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')
    pre_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, verbose_name='父评论id')
    operator = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'alarm_comment'
