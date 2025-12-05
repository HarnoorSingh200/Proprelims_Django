# quiz/admin.py
from django.contrib import admin
from ...models import UserProfile, QuizAttempt

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'percentage', 'attempt_date')
    list_filter = ('quiz', 'attempt_date')
    search_fields = ('user__username', 'quiz__quiz_name')