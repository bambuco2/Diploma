# Generated by Django 3.2.3 on 2021-11-25 12:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webstore', '0004_product_rank'),
    ]

    operations = [
        migrations.AddField(
            model_name='productincategory',
            name='subCategoryID',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='webstore.subcategory'),
            preserve_default=False,
        ),
    ]
