# Generated by Django 3.1.5 on 2023-10-18 14:40

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('om_logsearch', '0007_auto_20231017_1701'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppPass',
            fields=[
                ('id', models.AutoField(db_column='id', help_text='主键ID', primary_key=True, serialize=False)),
                ('name', models.CharField(db_column='name', help_text='名称', max_length=64, null=True)),
                ('created_at', models.DateTimeField(db_column='created_at', default=django.utils.timezone.now, help_text='创建时间', null=True)),
                ('created_by', models.CharField(db_column='created_by', default='sys', help_text='创建者', max_length=32, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at', help_text='更新时间')),
                ('updated_by', models.CharField(db_column='updated_by', default='sys', help_text='更新者', max_length=32, null=True)),
                ('component', models.CharField(blank=True, help_text='组件', max_length=32, null=True)),
                ('app', models.CharField(help_text='app', max_length=128)),
                ('uri', models.CharField(blank=True, help_text='正则字符', max_length=64, null=True)),
                ('end_time', models.DateTimeField(blank=True, help_text='忽略结束时间', null=True)),
                ('node', models.CharField(blank=True, help_text='备注', max_length=128, null=True)),
            ],
            options={
                'verbose_name': 'l_apppass',
                'verbose_name_plural': 'l_apppass',
                'db_table': 'l_apppass',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='GatePass',
            fields=[
                ('id', models.AutoField(db_column='id', help_text='主键ID', primary_key=True, serialize=False)),
                ('name', models.CharField(db_column='name', help_text='名称', max_length=64, null=True)),
                ('created_at', models.DateTimeField(db_column='created_at', default=django.utils.timezone.now, help_text='创建时间', null=True)),
                ('created_by', models.CharField(db_column='created_by', default='sys', help_text='创建者', max_length=32, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at', help_text='更新时间')),
                ('updated_by', models.CharField(db_column='updated_by', default='sys', help_text='更新者', max_length=32, null=True)),
                ('component', models.CharField(blank=True, help_text='组件', max_length=32, null=True)),
                ('domain', models.CharField(help_text='域名', max_length=128)),
                ('uri', models.CharField(blank=True, help_text='正则字符', max_length=64, null=True)),
                ('end_time', models.DateTimeField(blank=True, help_text='忽略结束时间', null=True)),
                ('node', models.CharField(blank=True, help_text='备注', max_length=128, null=True)),
            ],
            options={
                'verbose_name': 'l_gatepass',
                'verbose_name_plural': 'l_gatepass',
                'db_table': 'l_gatepass',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='componentindex',
            name='datasource_id',
            field=models.IntegerField(default=1, help_text='数据源id'),
        ),
        migrations.AlterUniqueTogether(
            name='appconfig',
            unique_together={('app', 'component')},
        ),
        migrations.AlterUniqueTogether(
            name='componentindex',
            unique_together={('datasource_id', 'component')},
        ),
        migrations.AlterUniqueTogether(
            name='gateconfig',
            unique_together={('domain', 'component')},
        ),
    ]