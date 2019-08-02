# Generated by Django 2.0.3 on 2019-02-17 00:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zip', models.CharField(max_length=10)),
                ('name', models.CharField(blank=True, max_length=50)),
                ('county', models.CharField(blank=True, max_length=50)),
                ('country', models.CharField(blank=True, max_length=50)),
                ('longitude', models.DecimalField(decimal_places=3, max_digits=8)),
                ('latitude', models.DecimalField(decimal_places=3, max_digits=8)),
            ],
        ),
    ]