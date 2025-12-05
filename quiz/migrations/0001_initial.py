# quiz/migrations/0001_initial.py
import django.db.models.deletion
from django.db import migrations, models
from django.conf import settings

class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('quiz_id', models.IntegerField(primary_key=True, serialize=False)),
                ('quiz_name', models.TextField()),
                ('exam_tags', models.JSONField()),
                ('requires_signup', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'quiz',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='QuestionSet',
            fields=[
                ('quiz', models.OneToOneField(db_column='quiz_id', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='quiz.quiz')),
                ('questions', models.JSONField()),
            ],
            options={
                'db_table': 'questions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='QuizAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField()),
                ('total_questions', models.IntegerField()),
                ('percentage', models.FloatField()),
                ('answers', models.JSONField()),
                ('attempt_date', models.DateTimeField(auto_now_add=True)),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.quiz')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quiz_attempts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'quiz_attempts',
                'ordering': ['-attempt_date'],
            },
        ),
    ]