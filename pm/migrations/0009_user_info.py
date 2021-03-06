# Generated by Django 3.1.3 on 2021-04-03 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pm', '0008_pm_manual'),
    ]

    operations = [
        migrations.CreateModel(
            name='user_info',
            fields=[
                ('no', models.AutoField(primary_key=True, serialize=False)),
                ('userid', models.CharField(max_length=255)),
                ('username', models.CharField(max_length=255)),
                ('userteam', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('useremail', models.CharField(max_length=255)),
                ('auth1', models.CharField(max_length=255)),
                ('auth2', models.CharField(max_length=255)),
                ('auth3', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'user_info',
                'managed': False,
            },
        ),
    ]
