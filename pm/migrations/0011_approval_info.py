# Generated by Django 3.1.3 on 2021-04-13 03:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pm', '0010_auto_20210403_2306'),
    ]

    operations = [
        migrations.CreateModel(
            name='approval_info',
            fields=[
                ('no', models.AutoField(primary_key=True, serialize=False)),
                ('division', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
                ('auth_name', models.CharField(max_length=255)),
                ('code_no', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'approval_info',
                'managed': False,
            },
        ),
    ]
