# Generated by Django 3.1.3 on 2021-03-15 04:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pm', '0005_pmsheetdb'),
    ]

    operations = [
        migrations.CreateModel(
            name='pm_sch',
            fields=[
                ('no', models.AutoField(primary_key=True, serialize=False)),
                ('controlno', models.CharField(max_length=255)),
                ('pmsheetno', models.CharField(max_length=255)),
                ('pmcode', models.CharField(max_length=255)),
                ('date', models.CharField(max_length=255)),
                ('status', models.CharField(max_length=255)),
                ('revno', models.CharField(max_length=255)),
                ('revdate', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'pm_sch',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='pm_sch_temp',
            fields=[
                ('no', models.AutoField(primary_key=True, serialize=False)),
                ('controlno', models.CharField(max_length=255)),
                ('pmsheetno', models.CharField(max_length=255)),
                ('pmcode', models.CharField(max_length=255)),
                ('date', models.CharField(max_length=255)),
                ('status', models.CharField(max_length=255)),
                ('revno', models.CharField(max_length=255)),
                ('revdate', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'pm_sch_temp',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='pmchecksheet',
            fields=[
                ('no', models.AutoField(primary_key=True, serialize=False)),
                ('controlno', models.CharField(max_length=255)),
                ('pmsheetno', models.CharField(max_length=255)),
                ('date', models.CharField(max_length=255)),
                ('pmcode', models.CharField(max_length=255)),
                ('item', models.TextField()),
                ('check', models.TextField()),
                ('result', models.TextField()),
                ('pass_y', models.CharField(max_length=255)),
                ('fail_y', models.CharField(max_length=255)),
                ('fail_n', models.CharField(max_length=255)),
                ('fail_result', models.TextField()),
                ('remark', models.TextField()),
            ],
            options={
                'db_table': 'pmchecksheet',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='pmchecksheet_temp',
            fields=[
                ('no', models.AutoField(primary_key=True, serialize=False)),
                ('controlno', models.CharField(max_length=255)),
                ('pmsheetno', models.CharField(max_length=255)),
                ('date', models.CharField(max_length=255)),
                ('pmcode', models.CharField(max_length=255)),
                ('item', models.TextField()),
                ('check', models.TextField()),
                ('result', models.TextField()),
                ('pass_y', models.CharField(max_length=255)),
                ('fail_y', models.CharField(max_length=255)),
                ('fail_n', models.CharField(max_length=255)),
                ('fail_result', models.TextField()),
                ('remark', models.TextField()),
            ],
            options={
                'db_table': 'pmchecksheet_temp',
                'managed': False,
            },
        ),
    ]
