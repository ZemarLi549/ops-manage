# Generated by Django 3.1.5 on 2023-10-17 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('om_logsearch', '0004_auto_20231016_2304'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComponentIndex',
            fields=[
                ('id', models.AutoField(db_column='id', help_text='主键ID', primary_key=True, serialize=False)),
                ('component', models.CharField(blank=True, help_text='组件', max_length=32, null=True)),
                ('index_str', models.CharField(help_text='索引正则', max_length=128)),
                ('time_field', models.IntegerField(blank=True, help_text='时间字段', null=True)),
                ('field_type', models.CharField(default='nginx', help_text='字段类型', max_length=4)),
                ('source', models.CharField(help_text='数据源类型，es,sls,cls,...', max_length=32)),
            ],
            options={
                'verbose_name': 'l_component',
                'verbose_name_plural': 'l_component',
                'db_table': 'l_component',
                'managed': True,
            },
        ),
    ]