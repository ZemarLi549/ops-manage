# Generated by Django 3.1.5 on 2023-11-15 14:30

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AlarmSolution',
            fields=[
                ('id', models.AutoField(db_column='id', help_text='主键ID', primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at', help_text='创建时间')),
                ('created_by', models.CharField(db_column='created_by', default='sys', help_text='创建者', max_length=32, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at', help_text='更新时间')),
                ('updated_by', models.CharField(db_column='updated_by', default='sys', help_text='更新者', max_length=32, null=True)),
                ('reach', models.CharField(blank=True, max_length=1500, null=True)),
                ('reason', models.CharField(blank=True, max_length=500, null=True)),
                ('solution', models.CharField(blank=True, max_length=500, null=True)),
            ],
            options={
                'db_table': 'alarm_solution',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AlarmConfig',
            fields=[
                ('id', models.IntegerField(db_column='id', help_text='主键ID', primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(db_column='created_at', default=django.utils.timezone.now, help_text='创建时间', null=True)),
                ('created_by', models.CharField(db_column='created_by', default='sys', help_text='创建者', max_length=32, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at', help_text='更新时间')),
                ('updated_by', models.CharField(db_column='updated_by', default='sys', help_text='更新者', max_length=32, null=True)),
                ('name', models.CharField(blank=True, help_text='名称', max_length=32, null=True)),
                ('alarm_to', models.JSONField(blank=True, default=[], null=True)),
                ('rule_name', models.CharField(blank=True, db_index=True, help_text='AlarmRule名称', max_length=32, null=True)),
                ('desc', models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={
                'db_table': 'alarm_config',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='AlarmIdentity',
            fields=[
                ('id', models.AutoField(db_column='id', default=1000, help_text='主键ID', primary_key=True, serialize=False)),
                ('identity', models.CharField(blank=True, max_length=250, null=True)),
                ('identity_tag_kv', models.JSONField(blank=True, default=dict, null=True)),
                ('times', models.IntegerField(blank=True, null=True)),
                ('score', models.IntegerField(blank=True, null=True)),
                ('status', models.IntegerField(choices=[('0', '消除'), ('1', '正在处理'), ('2', '处理完成'), ('3', '暂时忽略'), ('4', '未处理')], default='4', help_text='状态')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at', help_text='创建时间')),
                ('created_by', models.CharField(db_column='created_by', default='sys', help_text='创建者', max_length=32, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at', help_text='更新时间')),
                ('updated_by', models.CharField(db_column='updated_by', default='sys', help_text='更新者', max_length=32, null=True)),
                ('ignore_to', models.DateTimeField(blank=True, help_text='忽略截至时间', null=True)),
                ('handler', models.CharField(blank=True, help_text='处理人', max_length=250, null=True)),
            ],
            options={
                'db_table': 'alarm_identity',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='AlarmRule',
            fields=[
                ('id', models.AutoField(db_column='id', help_text='主键ID', primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at', help_text='创建时间')),
                ('created_by', models.CharField(db_column='created_by', default='sys', help_text='创建者', max_length=32, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at', help_text='更新时间')),
                ('updated_by', models.CharField(db_column='updated_by', default='sys', help_text='更新者', max_length=32, null=True)),
                ('name', models.CharField(db_index=True, max_length=32, unique=True)),
                ('rule_keys', models.CharField(blank=True, help_text='组成指纹的几个key', max_length=64)),
                ('rule_re', models.CharField(blank=True, help_text='从告警内容取key加入指纹', max_length=64)),
                ('rate', models.IntegerField(default=1, help_text='基础评分')),
                ('freq', models.CharField(blank=True, help_text='告警频率', max_length=32, null=True)),
                ('desc', models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={
                'db_table': 'alarm_rule',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='AlarmUser',
            fields=[
                ('id', models.AutoField(db_column='id', help_text='主键ID', primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at', help_text='创建时间')),
                ('created_by', models.CharField(db_column='created_by', default='sys', help_text='创建者', max_length=32, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at', help_text='更新时间')),
                ('updated_by', models.CharField(db_column='updated_by', default='sys', help_text='更新者', max_length=32, null=True)),
                ('name', models.CharField(blank=True, help_text='中文名称', max_length=32, null=True)),
                ('username', models.CharField(db_index=True, max_length=32, unique=True)),
                ('phone', models.CharField(blank=True, max_length=24, null=True)),
                ('email', models.CharField(blank=True, max_length=32, null=True)),
                ('desc', models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={
                'db_table': 'alarm_user',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='AlarmComment',
            fields=[
                ('id', models.AutoField(db_column='id', help_text='主键ID', primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at', help_text='创建时间')),
                ('created_by', models.CharField(db_column='created_by', default='sys', help_text='创建者', max_length=32, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at', help_text='更新时间')),
                ('updated_by', models.CharField(db_column='updated_by', default='sys', help_text='更新者', max_length=32, null=True)),
                ('comment_content', models.JSONField(verbose_name='评论内容')),
                ('comment_time', models.DateTimeField(auto_now_add=True, verbose_name='评论时间')),
                ('identity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alarm_comment', to='om_alarm.alarmidentity', verbose_name='指纹')),
                ('pre_comment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='om_alarm.alarmcomment', verbose_name='父评论id')),
            ],
            options={
                'db_table': 'alarm_comment',
                'managed': True,
            },
        ),
    ]
