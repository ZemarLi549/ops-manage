from django.db import models
from django.utils.timezone import now
# from django.db.backends.mysql.base import DatabaseWrapper
# DatabaseWrapper.data_types['DateTimeField'] = 'datetime'

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
    name = models.CharField(db_column='name', help_text='名称', max_length=64, null=True,blank=True,db_index=True)
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


class Status(models.IntegerChoices):
    FOBBIDEN = 0
    ACTIVATE = 1
    STORE = 2

class User(BaseModel):
    status = models.IntegerField(db_column='status', help_text='0：禁用； 1：激活； 2：归档', choices=Status.choices, default=1)
    password = models.CharField(db_column='password', help_text='password', max_length=128, null=True)
    realname = models.CharField(max_length=128, null=True, blank=True)
    head_img = models.CharField(max_length=2048, null=True, blank=True)
    phone = models.CharField( max_length=128, null=True, blank=True)
    dept_power = models.BooleanField(default=True)
    remark = models.CharField( max_length=128, null=True, blank=True)
    email = models.CharField( max_length=128, null=True, blank=True)
    department_id = models.IntegerField(db_column='department_id', help_text='部门ID',  default=0)
    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = verbose_name = '用户'
        managed = True
        db_table = 'om_user'

class Role(BaseModel):
    description = models.CharField(db_column='description', help_text='描述', max_length=256, null=True)
    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = verbose_name = '角色'
        managed = True
        db_table = 'om_role'

class User_Role(BaseModel):
    user_id= models.IntegerField(db_column='user_id', help_text='用户ID',  null=True)
    role_id=models.IntegerField(db_column='role_id', help_text='角色ID',  null=True)
    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = verbose_name = '用户角色'
        managed = True
        db_table = 'om_user_role'


class MenuType(models.IntegerChoices):
    DIR = 0
    MENU = 1
    POWER = 2
class Resource(BaseModel):
    icon = models.CharField(max_length=128, null=True,blank=True)
    is_show = models.BooleanField(default=True)
    keepalive = models.BooleanField(default=True)
    order_num = models.IntegerField(null=True)
    perms= models.CharField(max_length=256, null=True)## 前端对应的code
    router= models.CharField(max_length=256, null=True)
    type= models.IntegerField(default=0)#MenuType
    view_path= models.CharField(max_length=256, null=True)
    parent_id= models.IntegerField(db_column='parent_id', help_text='父ID',  null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = verbose_name = '资源'
        managed = True
        db_table = 'om_resource'

class Department(BaseModel):
    description = models.CharField(db_column='description', help_text='描述', max_length=16, null=True)
    parent_id= models.IntegerField(db_column='parent_id', help_text='父ID',  null=True)
    order_num = models.IntegerField(db_column='order_num', help_text='paixu', null=True)
    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = verbose_name = '部门'
        managed = True
        db_table = 'om_dept'

class Permissions(models.IntegerChoices):
    YES = 1
    NO = 0
class Resource_Role(BaseModel):
    menu_id=models.IntegerField(db_column='menu_id', help_text='资源ID',  null=True)
    role_id=models.IntegerField(db_column='role_id', help_text='角色ID',  null=True)
    permission= models.IntegerField(db_column='permissions', help_text='0：没有； 1：有', choices=Permissions.choices, default=0)
    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = verbose_name = '资源角色'
        managed = True
        db_table = 'om_resource_role'

class Department_Role(BaseModel):
    department_id=models.IntegerField(db_column='department_id', help_text='部门ID',  null=True)
    role_id=models.IntegerField(db_column='role_id', help_text='角色ID',  null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = verbose_name = '部门角色'
        managed = True
        db_table = 'om_dept_role'


class OpsToken(models.Model):
    token = models.CharField(db_column='token', help_text='token', max_length=128, null=False,unique=True)
    role = models.OneToOneField('Role', on_delete=models.CASCADE,to_field='id')
    id = models.AutoField(
        db_column='id', help_text='主键ID', primary_key=True)
    created_at = models.DateTimeField(
        db_column='created_at', help_text='创建时间', default=now, null=True)
    created_by = models.CharField(
        default="sys", db_column='created_by', help_text='创建者', max_length=32, null=True)
    updated_at = models.DateTimeField(
        db_column='updated_at', help_text='更新时间', auto_now=True)
    updated_by = models.CharField(
        default="sys", db_column='updated_by', help_text='更新者', max_length=32, null=True)
    def __str__(self):
        return str(self.token)

    class Meta:
        verbose_name_plural = verbose_name = 'opstoken'
        managed = True
        db_table = 'opstoken'

