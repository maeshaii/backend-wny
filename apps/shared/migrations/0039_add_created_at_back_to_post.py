# Generated manually to fix created_at field issue

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0038_ensure_ojt_end_date_column_final'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='post',
                    name='created_at',
                    field=models.DateTimeField(auto_now_add=True),
                ),
            ],
            database_operations=[
                # No database operations since column already exists
            ],
        ),
    ]
