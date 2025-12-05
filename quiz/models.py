from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User


class RecommendedBook(models.Model):
    title = models.TextField()
    link = models.TextField()

    class Meta:
        db_table = 'affilate'

    def __str__(self):
        return self.title

class SuperQuiz(models.Model):
    quiz_id = models.IntegerField(primary_key=True)
    quiz_name = models.TextField()
    exam_tags = models.JSONField()
    requires_signup = models.BooleanField(default=True)
    part_count = models.IntegerField(default=4)
    questions_per_part = models.IntegerField(default=25)
    total_questions = models.IntegerField(default=100)
    part_names = models.JSONField(default=dict)

    class Meta:
        managed = False
        db_table = 'super_quiz'

    def __str__(self):
        return self.quiz_name

class SuperQuestionSet(models.Model):
    id = models.BigAutoField(primary_key=True)
    quiz = models.ForeignKey(SuperQuiz, on_delete=models.DO_NOTHING, db_column='quiz_id')
    part_number = models.IntegerField()
    questions = models.JSONField()

    class Meta:
        managed = False
        db_table = 'super_questions'
        unique_together = ('quiz', 'part_number')

class SuperQuizAttempt(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='super_quiz_attempts')
    quiz = models.ForeignKey(SuperQuiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    percentage = models.FloatField()
    attempt_date = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    total_score = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'super_quiz_attempts'
        ordering = ['-attempt_date']

    def __str__(self):
        return f"{self.user.username} - {self.quiz.quiz_name} - Part {self.part_number}"

class AdvanceQuiz(models.Model):
    quiz_id = models.IntegerField(primary_key=True)
    quiz_name = models.TextField()
    exam_tags = models.JSONField()
    requires_signup = models.BooleanField(default=True)
    question_count = models.IntegerField(default=25)

    class Meta:
        managed = False
        db_table = 'advance_quiz'


class AdvanceQuestionSet(models.Model):
    quiz = models.OneToOneField('AdvanceQuiz', on_delete=models.DO_NOTHING, db_column='quiz_id', primary_key=True)
    questions = models.JSONField()

    class Meta:
        managed = False
        db_table = 'advance_questions'

class AdvanceQuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='advance_quiz_attempts')
    quiz = models.ForeignKey(AdvanceQuiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    percentage = models.FloatField()
    answers = models.JSONField()
    attempt_date = models.DateTimeField(auto_now_add=True)
    total_score = models.IntegerField()

    class Meta:
        db_table = 'advance_quiz_attempts'
        ordering = ['-attempt_date']

    def __str__(self):
        return f"{self.user.username} - {self.quiz.quiz_name} - {self.attempt_date}"

class BlogPost(models.Model):
    post_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    likes = models.ManyToManyField(User, related_name='blog_likes', blank=True)

    class Meta:
        db_table = 'blog_posts'
        ordering = ['-post_id']

    def __str__(self):
        return self.title

    def like_count(self):
        return self.likes.count()

class Quiz(models.Model):
    quiz_id = models.IntegerField(primary_key=True)
    quiz_name = models.TextField()
    exam_tags = models.JSONField()
    requires_signup = models.BooleanField(default=True)
    question_count = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'quiz'


class QuestionSet(models.Model):
    quiz = models.OneToOneField('Quiz', on_delete=models.DO_NOTHING, db_column='quiz_id', primary_key=True)
    questions = models.JSONField()

    class Meta:
        managed = False
        db_table = 'questions'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    terms_accepted_at = models.DateTimeField(null=True, blank=True)  # ← NEW FIELD

    def __str__(self):
        return f"{self.user.username}'s Profile"


class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    percentage = models.FloatField()
    answers = models.JSONField()
    attempt_date = models.DateTimeField(auto_now_add=True)
    total_score = models.IntegerField()

    class Meta:
        db_table = 'quiz_attempts'
        ordering = ['-attempt_date']

    def __str__(self):
        return f"{self.user.username} - {self.quiz.quiz_name} - {self.attempt_date}"

class Meta:
    db_table = 'quiz_attempts'
    ordering = ['-attempt_date']
    unique_together = ('user', 'quiz')

