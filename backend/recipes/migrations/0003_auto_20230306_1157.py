# Generated by Django 2.2.19 on 2023-03-06 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20230306_0837'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=64, verbose_name='название'),
        ),
    ]
