# Generated by Django 2.0.2 on 2018-03-18 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0004_remove_image_like_num'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='stauts',
            field=models.IntegerField(default=0),
        ),
    ]