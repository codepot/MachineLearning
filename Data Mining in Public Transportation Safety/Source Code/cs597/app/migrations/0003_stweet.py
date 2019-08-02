# Generated by Django 2.0.3 on 2019-03-30 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20190217_0051'),
    ]

    operations = [
        migrations.CreateModel(
            name='sTweet',
            fields=[
                ('tid', models.AutoField(primary_key=True, serialize=False)),
                ('text', models.TextField(blank=True, max_length=280)),
                ('longitude', models.DecimalField(blank=True, decimal_places=3, max_digits=8, null=True)),
                ('latitude', models.DecimalField(blank=True, decimal_places=3, max_digits=8, null=True)),
                ('address', models.CharField(blank=True, max_length=64)),
                ('signal', models.CharField(blank=True, max_length=10)),
                ('create_at', models.DateTimeField(blank=True)),
            ],
        ),
    ]
