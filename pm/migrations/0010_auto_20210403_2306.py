# Generated by Django 3.1.3 on 2021-04-03 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pm', '0009_user_info'),
    ]

    operations = [
        migrations.CreateModel(
            name='userinfo',
            fields=[
                ('no', models.AutoField(primary_key=True, serialize=False)),
                ('userid', models.CharField(max_length=255)),
                ('username', models.CharField(max_length=255)),
                ('userteam', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('useremail', models.CharField(max_length=255)),
                ('auth1', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'userinfo',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='workorder',
            fields=[
                ('no', models.AutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=255)),
                ('capa', models.CharField(max_length=255)),
                ('requestor', models.CharField(max_length=255)),
                ('team', models.CharField(max_length=255)),
                ('controlno', models.CharField(max_length=255)),
                ('equipname', models.CharField(max_length=255)),
                ('roomname', models.CharField(max_length=255)),
                ('roomno', models.CharField(max_length=255)),
                ('description', models.TextField(max_length=255)),
                ('req_date', models.CharField(max_length=255)),
                ('req_reason', models.TextField(max_length=255)),
                ('date', models.CharField(max_length=255)),
                ('r_t_name', models.CharField(max_length=255)),
                ('r_t_date', models.CharField(max_length=255)),
                ('r_s_name', models.CharField(max_length=255)),
                ('r_s_date', models.CharField(max_length=255)),
                ('r_m_name', models.CharField(max_length=255)),
                ('r_m_date', models.CharField(max_length=255)),
                ('r_q_name', models.CharField(max_length=255)),
                ('r_q_date', models.CharField(max_length=255)),
                ('r_attach', models.CharField(max_length=255)),
                ('status', models.CharField(max_length=255)),
                ('workorderno', models.CharField(max_length=255)),
                ('date_init', models.CharField(max_length=255)),
                ('work_desc', models.TextField(max_length=255)),
                ('action_name', models.CharField(max_length=255)),
                ('action_company', models.CharField(max_length=255)),
                ('action_date', models.CharField(max_length=255)),
                ('test_result', models.TextField(max_length=255)),
                ('usedpart', models.CharField(max_length=255)),
                ('pm_trans', models.CharField(max_length=255)),
                ('w_s_name', models.CharField(max_length=255)),
                ('w_s_date', models.CharField(max_length=255)),
                ('w_m_name', models.CharField(max_length=255)),
                ('w_m_date', models.CharField(max_length=255)),
                ('w_q_name', models.CharField(max_length=255)),
                ('w_q_date', models.CharField(max_length=255)),
                ('repair_type', models.CharField(max_length=255)),
                ('detail_type', models.CharField(max_length=255)),
                ('repair_method', models.TextField(max_length=255)),
                ('codeno_temp', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'workorder',
                'managed': False,
            },
        ),
        migrations.DeleteModel(
            name='user_info',
        ),
    ]
