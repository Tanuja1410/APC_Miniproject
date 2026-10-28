from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("trips", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="expense",
            name="participants",
            field=models.ManyToManyField(
                blank=True,
                related_name="shared_expenses",
                to="trips.member",
            ),
        ),
    ]
