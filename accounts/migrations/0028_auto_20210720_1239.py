# Generated by Django 3.2.3 on 2021-07-20 07:09

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0027_query'),
    ]

    operations = [
        migrations.AddField(
            model_name='query',
            name='status',
            field=models.CharField(choices=[('Not replied', 'Not replied'), ('Replied', 'Replied')], default='Not replied', max_length=100),
        ),
        migrations.AlterField(
            model_name='query',
            name='datetime',
            field=models.DateField(blank=True, default=datetime.datetime(2021, 7, 20, 12, 39, 53, 313650), null=True),
        ),
        migrations.AlterField(
            model_name='query',
            name='receiver',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to='accounts.staff'),
        ),
        migrations.AlterField(
            model_name='query',
            name='sender',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sender', to='accounts.student'),
        ),
    ]
