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
    name = models.CharField(db_column='name', help_text='镜像名称', max_length=64, null=True,db_index=True)
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


class Cluster(BaseModel):
    config = models.TextField(blank=True,null=True)
    version = models.CharField(max_length=64, null=True, blank=True)
    desc = models.CharField(max_length=128, null=True, blank=True)
    def __str__(self):
        return str(self.id)

    class Meta:
        managed = True
        db_table = 'k8s_cluster'