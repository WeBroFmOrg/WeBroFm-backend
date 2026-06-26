from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0005_make_audio_file_key_optional'),
    ]

    operations = [
        # Remove old data first (no production teasers expected)
        migrations.RunSQL("DELETE FROM content_teaser", reverse_sql=migrations.RunSQL.noop),

        # Remove old FK and fields
        migrations.RemoveField(
            model_name='teaser',
            name='show',
        ),
        migrations.RemoveField(
            model_name='teaser',
            name='video_key',
        ),
        migrations.RemoveField(
            model_name='teaser',
            name='thumbnail_key',
        ),
        migrations.RemoveField(
            model_name='teaser',
            name='duration_seconds',
        ),

        # Alter existing fields
        migrations.AlterField(
            model_name='teaser',
            name='title',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='teaser',
            name='sequence',
            field=models.PositiveIntegerField(default=0),
        ),

        # Add new fields
        migrations.AddField(
            model_name='teaser',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='teasers/images/'),
        ),
        migrations.AddField(
            model_name='teaser',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='teaser',
            name='is_converted',
            field=models.BooleanField(default=False, help_text='Has been turned into a show'),
        ),
        migrations.AddField(
            model_name='teaser',
            name='converted_show',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='converted_from_teaser', to='content.show'),
        ),
    ]
