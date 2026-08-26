# Generated for the Payment model (Paystack integration).

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=50)),
                ('reference', models.CharField(max_length=100, unique=True)),
                ('amount_kobo', models.PositiveIntegerField(help_text='Amount in kobo (₦1 = 100 kobo).')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')], default='pending', max_length=10)),
                ('paystack_payload', models.JSONField(blank=True, help_text="Raw response from Paystack's verify call, for audit.", null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('lead', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='leads.lead')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
