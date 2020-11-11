# Generated by Django 3.0.8 on 2020-09-01 09:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0032_auto_20200830_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopcart',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.Product')),
            ],
        ),
    ]