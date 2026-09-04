# Removes the Payment model (Book Consultation / Paystack removed) and adds
# the Subscriber model for the newsletter signup feature.
#
# WARNING: this DeleteModel operation drops the payments table and any rows
# in it. If the live Render database holds real payment records, back that
# table up before running `migrate` in production.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0002_payment'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Payment',
        ),
        migrations.CreateModel(
            name='Subscriber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
