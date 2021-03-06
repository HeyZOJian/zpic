# Generated by Django 2.0.2 on 2018-03-15 04:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_auto_20180225_1437'),
    ]

    operations = [
        migrations.AddField(
            model_name='userrelationship',
            name='create_time',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterUniqueTogether(
            name='userrelationship',
            unique_together={('user_a', 'user_b', 'relation_type', 'create_time')},
        ),
    ]
