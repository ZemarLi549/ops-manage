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
    name = models.CharField(db_column='name', help_text='名称', max_length=64, null=True)
    created_at = models.DateTimeField(
        db_column='created_at', help_text='创建时间', default=now, null=True)
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


class DataSource(BaseModel):
    source = models.CharField(help_text='数据源类型，es,sls,cls,...', max_length=32, null=False, blank=False)
    # es存储字段
    host = models.CharField(help_text='es地址', max_length=128, null=True, blank=True)
    username = models.CharField(help_text='es用户名', max_length=128, null=True, blank=True)
    password = models.CharField(help_text='es密码', max_length=128, null=True, blank=True)

    # 云存储字段
    project_name = models.CharField(help_text='项目名称', max_length=128, null=True, blank=True)
    logstore = models.CharField(help_text='仓库名', max_length=128, null=True, blank=True)
    region = models.CharField(help_text='区域', max_length=128, null=True, blank=True)
    alisecret = models.CharField(help_text='密钥', max_length=128, null=True, blank=True)
    alikey = models.CharField(help_text='KEY', max_length=128, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = verbose_name = '数据源信息'
        managed = True
        db_table = 'l_datasource'


class GateConfig(BaseModel):
    domain = models.CharField(help_text='域名', max_length=128, null=False)
    component = models.CharField(help_text='组件', max_length=32, null=True, blank=True)
    datasource_id = models.IntegerField(help_text='数据源id', null=False)
    isblack = models.CharField(help_text='isblack', max_length=4, default='n')

    def __str__(self):
        return str(self.id)

    class Meta:
        unique_together = ('domain', 'component')
        verbose_name_plural = verbose_name = '网关日志'
        managed = True
        db_table = 'l_gateconfig'


class AppConfig(BaseModel):
    app = models.CharField(help_text='服务名', max_length=64, null=False)
    component = models.CharField(help_text='组件', max_length=32, null=True, blank=True)
    datasource_id = models.IntegerField(help_text='数据源id', null=False)
    isblack = models.CharField(help_text='isblack', max_length=4, default='n')

    def __str__(self):
        return str(self.id)

    class Meta:
        unique_together = ('app', 'component')
        verbose_name_plural = verbose_name = '服务日志'
        managed = True
        db_table = 'l_appconfig'


class ComponentIndex(BaseModel):
    component = models.CharField(help_text='组件', max_length=32, null=True, blank=True)
    index_str = models.CharField(help_text='索引正则', max_length=128, null=False)
    time_field = models.CharField(help_text='时间字段', max_length=16, null=True, blank=True)
    # nginxlog,applog
    field_type = models.CharField(help_text='字段类型', max_length=16, null=True, blank=True)
    source = models.CharField(help_text='数据源类型，es,sls,cls,...', max_length=32, null=False, blank=False)
    datasource_id = models.IntegerField(help_text='数据源id', null=False, default=1)

    def __str__(self):
        return str(self.id)

    class Meta:
        unique_together = ('datasource_id', 'component')
        verbose_name_plural = verbose_name = 'l_component'
        managed = True
        db_table = 'l_component'


class GatePass(BaseModel):
    component = models.CharField(help_text='组件', max_length=32, null=True, blank=True)
    domain = models.CharField(help_text='域名', max_length=128, null=False)
    uri = models.CharField(help_text='正则字符', max_length=64, null=True, blank=True)
    end_time = models.DateTimeField(help_text='忽略结束时间', null=True, blank=True)
    note = models.CharField(help_text='备注', max_length=128, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = verbose_name = 'l_gatepass'
        managed = True
        db_table = 'l_gatepass'


class AppPass(BaseModel):
    component = models.CharField(help_text='组件', max_length=32, null=True, blank=True)
    app = models.CharField(help_text='app', max_length=128, null=False)
    uri = models.CharField(help_text='正则字符', max_length=64, null=True, blank=True)
    end_time = models.DateTimeField(help_text='忽略结束时间', null=True, blank=True)
    note = models.CharField(help_text='备注', max_length=128, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = verbose_name = 'l_apppass'
        managed = True
        db_table = 'l_apppass'
