# Generated by Django 3.2.3 on 2021-12-17 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webstore', '0006_tag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='tag',
            field=models.CharField(max_length=300, unique=True),
        ),
    ]
