from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Trip",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("budget", models.FloatField(default=0)),
                ("start_date", models.DateField(blank=True, null=True)),
                ("end_date", models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Member",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("mobile", models.CharField(blank=True, max_length=20)),
                ("trip", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="members", to="trips.trip")),
            ],
        ),
        migrations.CreateModel(
            name="Expense",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("amount", models.FloatField()),
                ("category", models.CharField(default="Other", max_length=50)),
                ("created_at", models.DateField(auto_now_add=True)),
                ("description", models.TextField(blank=True)),
                ("paid_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payments", to="trips.member")),
                ("trip", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="expenses", to="trips.trip")),
            ],
        ),
    ]
