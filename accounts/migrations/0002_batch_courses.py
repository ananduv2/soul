# Generated by Django 3.2.3 on 2021-07-12 11:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Courses',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300, null=True)),
                ('fee', models.CharField(max_length=6)),
            ],
        ),
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timing', models.CharField(max_length=100, null=True)),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True)),
                ('mode', models.CharField(choices=[('1', 'Weekday'), ('2', 'Weekend')], default=1, max_length=100)),
                ('status', models.CharField(choices=[('1', 'Yet to start'), ('2', 'Ongoing'), ('3', 'Completed')], default=1, max_length=100)),
                ('subject', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.courses')),
                ('trainer', models.ForeignKey(limit_choices_to={'is_trainer': True}, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.staff')),
            ],
        ),
    ]
