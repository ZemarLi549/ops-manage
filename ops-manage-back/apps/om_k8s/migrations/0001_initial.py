# Generated by Django 3.1.5 on 2022-11-30 15:13

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('id', models.AutoField(db_column='id', help_text='主键ID', primary_key=True, serialize=False)),
                ('name', models.CharField(db_column='name', db_index=True, help_text='镜像名称', max_length=64, null=True)),
                ('created_at', models.DateTimeField(db_column='created_at', default=django.utils.timezone.now, help_text='创建时间', null=True)),
                ('created_by', models.CharField(db_column='created_by', default='sys', help_text='创建者', max_length=32, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at', help_text='更新时间')),
                ('updated_by', models.CharField(db_column='updated_by', default='sys', help_text='更新者', max_length=32, null=True)),
                ('config', models.TextField(blank=True, null=True)),
                ('version', models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={
                'db_table': 'k8s_cluster',
                'managed': True,
            },
        ),
    ]