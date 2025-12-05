from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django_htmx.http import HttpResponseClientRedirect
from django.urls import reverse
from functools import wraps
from django.core.paginator import Paginator
from .models import Quiz, QuestionSet, QuizAttempt, UserProfile
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
from django.db.models import Q
from .models import Quiz
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from .models import UserProfile
from .models import BlogPost
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.html import escape
from django_ratelimit.decorators import ratelimit
from django.http import HttpResponse
from django.db.models import Exists, OuterRef
from django.db.models import Value, BooleanField
from .models import AdvanceQuiz, AdvanceQuestionSet, AdvanceQuizAttempt
from .models import SuperQuiz, SuperQuestionSet, SuperQuizAttempt
from .models import RecommendedBook


# Decorator for AdvanceQuiz login requirement
def conditional_advance_quiz_login_required(view_func):
    """Decorator that requires login only if the advance quiz requires signup"""
    @wraps(view_func)
    def _wrapped_view(request, quiz_id, *args, **kwargs):
        quiz = get_object_or_404(AdvanceQuiz, quiz_id=quiz_id)
        if quiz.requires_signup and not request.user.is_authenticated:
            messages.info(request, 'Please sign in to take this advance quiz.')
            return redirect('account_login')
        return view_func(request, quiz_id, *args, **kwargs)
    return _wrapped_view

# Advance Quiz Views
def advance_quiz_detail(request, quiz_id):
    """Advance quiz detail page with start quiz functionality"""
    quiz = get_object_or_404(AdvanceQuiz, quiz_id=quiz_id)
    if quiz.requires_signup and not request.user.is_authenticated:
        messages.info(request, 'Please sign in to take this advance quiz.')
        return redirect('account_login')
    if request.method == 'POST' or request.htmx:
        user_id = request.user.id if request.user.is_authenticated else 'anonymous'
        session_key = f'advance_{quiz_id}_answers_{user_id}'
        request.session[session_key] = {}
        if request.htmx:
            return HttpResponseClientRedirect(
                reverse('advance_quiz_paginated', kwargs={'quiz_id': quiz_id})
            )
        return redirect('advance_quiz_paginated', quiz_id=quiz_id)
    return render(request, 'quiz/advance_quiz_detail.html', {'quiz': quiz})

@conditional_advance_quiz_login_required
def advance_quiz_paginated(request, quiz_id):
    """Render advance quiz with paginated questions"""
    quiz = get_object_or_404(AdvanceQuiz, quiz_id=quiz_id)
    question_set = get_object_or_404(AdvanceQuestionSet, quiz_id=quiz_id)
    return render(request, 'quiz/advance_quiz_paginated.html', {
        'quiz': quiz,
        'questions': question_set.questions,
    })

@conditional_advance_quiz_login_required
@require_http_methods(["POST"])
@ratelimit(key='ip', rate='30/m', block=True)
def advance_quiz_submit_paginated(request, quiz_id):
    """Handle advance quiz submission and display results"""
    if getattr(request, 'limited', False):
        return HttpResponseTooManyRequests("Too many requests. Please slow down.")

    quiz = get_object_or_404(AdvanceQuiz, quiz_id=quiz_id)
    question_set = get_object_or_404(AdvanceQuestionSet, quiz_id=quiz_id)
    questions = question_set.questions

    try:
        answers = json.loads(request.POST.get('answers', '{}'))
        time_taken = int(request.POST.get('time_taken', 0))
    except (json.JSONDecodeError, ValueError):
        messages.error(request, "Invalid answers submitted.")
        return redirect('advance_quiz_paginated', quiz_id=quiz_id)

    score = 0
    results = []
    for i, q in enumerate(questions):
        user_ans = answers.get(str(i), '')
        correct = q['answer']
        is_correct = user_ans == correct
        if is_correct:
            score += 1
        results.append({
            'question': q['question'],
            'options': q['options'],
            'your_answer': user_ans,
            'correct_answer': correct,
            'is_correct': is_correct,
            'explanation': q.get('explanation', '')
        })

    percentage = (score / len(questions)) * 100 if questions else 0

    if request.user.is_authenticated:
        UserProfile.objects.get_or_create(user=request.user)
        AdvanceQuizAttempt.objects.update_or_create(
            user=request.user,
            quiz=quiz,
            defaults={
                'score': score,
                'total_questions': len(questions),
                'percentage': percentage,
                'answers': answers,
                'attempt_date': timezone.now(),
                'total_score': 25,
            }
        )

    recommended_books = RecommendedBook.objects.order_by('?')[:7]

    return render(request, 'quiz/advance_quiz_result.html', {
        'quiz': quiz,
        'score': score,
        'total': len(questions),
        'percentage': round(percentage, 1),
        'results': results,
        'time_taken': time_taken,
        'recommended_books': recommended_books
    })

def advance_quiz_solutions(request, quiz_id):
    """Display all questions with correct answers and explanations for an advance quiz"""
    quiz = get_object_or_404(AdvanceQuiz, quiz_id=quiz_id)
    question_set = get_object_or_404(AdvanceQuestionSet, quiz_id=quiz_id)
    questions = question_set.questions

    solutions = []
    for i, q in enumerate(questions):
        solutions.append({
            'question': q['question'],
            'options': q['options'],
            'correct_answer': q['answer'],
            'explanation': q.get('explanation', ''),
        })

    recommended_books = RecommendedBook.objects.order_by('?')[:7]

    return render(request, 'quiz/advance_quiz_solutions.html', {
        'quiz': quiz,
        'solutions': solutions,
        'total': len(questions),
        'recommended_books': recommended_books
    })



def conditional_super_quiz_login_required(view_func):
    """Decorator that requires login only if the super quiz requires signup"""
    @wraps(view_func)
    def _wrapped_view(request, quiz_id, *args, **kwargs):
        quiz = get_object_or_404(SuperQuiz, quiz_id=quiz_id)
        if quiz.requires_signup and not request.user.is_authenticated:
            messages.info(request, 'Please sign in to take this super quiz.')
            return redirect('account_login')
        return view_func(request, quiz_id, *args, **kwargs)
    return _wrapped_view

def super_quiz_detail(request, quiz_id):
    """Super quiz detail page with start quiz functionality"""
    quiz = get_object_or_404(SuperQuiz, quiz_id=quiz_id)
    if quiz.requires_signup and not request.user.is_authenticated:
        messages.info(request, 'Please sign in to take this super quiz.')
        return redirect('account_login')
    if request.method == 'POST' or request.htmx:
        return redirect('super_quiz_instructions', quiz_id=quiz_id)
    return render(request, 'quiz/super_quiz_instructions.html', {'quiz': quiz})

def super_quiz_instructions(request, quiz_id):
    """Instruction page for super quiz"""
    quiz = get_object_or_404(SuperQuiz, quiz_id=quiz_id)
    if quiz.requires_signup and not request.user.is_authenticated:
        messages.info(request, 'Please sign in to take this super quiz.')
        return redirect('account_login')
    if request.method == 'POST' or request.htmx:
        user_id = request.user.id if request.user.is_authenticated else 'anonymous'
        session_key = f'super_{quiz_id}_answers_{user_id}'
        request.session[session_key] = {}
        if request.htmx:
            return HttpResponseClientRedirect(
                reverse('super_quiz_paginated', kwargs={'quiz_id': quiz_id})
            )
        return redirect('super_quiz_paginated', quiz_id=quiz_id)
    return render(request, 'quiz/super_quiz_instructions.html', {'quiz': quiz})

@conditional_super_quiz_login_required
def super_quiz_paginated(request, quiz_id):
    """Render super quiz with section tabs"""
    quiz = get_object_or_404(SuperQuiz, quiz_id=quiz_id)
    question_sets = SuperQuestionSet.objects.filter(quiz_id=quiz_id).order_by('part_number')
    sections = []
    for qs in question_sets:
        part_name = quiz.part_names.get(str(qs.part_number), f"Part {qs.part_number}")
        sections.append({
            'part_number': qs.part_number,
            'part_name': part_name,
            'questions': qs.questions,
        })
    return render(request, 'quiz/super_quiz_paginated.html', {
        'quiz': quiz,
        'sections': sections,
    })

@conditional_super_quiz_login_required
@require_http_methods(["POST"])
@ratelimit(key='ip', rate='30/m', block=True)
def super_quiz_submit_paginated(request, quiz_id):
    """Handle super quiz submission and display results"""
    if getattr(request, 'limited', False):
        return HttpResponseTooManyRequests("Too many requests. Please slow down.")

    quiz = get_object_or_404(SuperQuiz, quiz_id=quiz_id)
    question_sets = SuperQuestionSet.objects.filter(quiz_id=quiz_id).order_by('part_number')
    try:
        answers = json.loads(request.POST.get('answers', '{}'))
        time_taken = int(request.POST.get('time_taken', 0))
    except (json.JSONDecodeError, ValueError):
        messages.error(request, "Invalid answers submitted.")
        return redirect('super_quiz_paginated', quiz_id=quiz_id)

    section_results = []
    total_score = 0
    total_questions = 0
    max_possible_marks = 0

    for qs in question_sets:
        questions = qs.questions
        part_number = qs.part_number
        part_name = quiz.part_names.get(str(part_number), f"Part {part_number}")
        score = 0  # Score in marks
        correct_count = 0
        wrong_count = 0
        results = []
        for i, q in enumerate(questions):
            user_ans = answers.get(f"{part_number}_{i}", '')
            correct = q['answer']
            is_correct = user_ans == correct
            if user_ans and is_correct:
                score += 2  # +2 for correct
                correct_count += 1
            elif user_ans and not is_correct:
                score -= 0.5  # -0.5 for wrong
                wrong_count += 1
            # Skipped questions (user_ans is empty) contribute 0 to score
            results.append({
                'question': q['question'],
                'options': q['options'],
                'your_answer': user_ans,
                'correct_answer': correct,
                'is_correct': is_correct,
                'explanation': q.get('explanation', ''),
            })
        total_questions_part = len(questions)
        max_marks_part = total_questions_part * 2  # Max marks per question is 2
        percentage = (score / max_marks_part * 100) if max_marks_part > 0 else 0
        section_results.append({
            'part_number': part_number,
            'part_name': part_name,
            'score': score,  # Score in marks
            'correct_count': correct_count,
            'wrong_count': wrong_count,
            'total': total_questions_part,
            'max_marks': max_marks_part,
            'percentage': round(percentage, 1),
            'results': results,
        })
        total_score += score
        total_questions += total_questions_part
        max_possible_marks += max_marks_part

    percentage = (total_score / 100) * 100
    if request.user.is_authenticated:
        SuperQuizAttempt.objects.update_or_create(
            user=request.user,
            quiz=quiz,
            defaults={
                'score': total_score,
                'total_questions': 100,
                'percentage': percentage,
                'attempt_date': timezone.now(),
                'is_completed': True,
                'total_score': 200
            }
        )

    overall_percentage = (total_score / max_possible_marks * 100) if max_possible_marks > 0 else 0

    recommended_books = RecommendedBook.objects.order_by('?')[:7]

    return render(request, 'quiz/super_quiz_result.html', {
        'quiz': quiz,
        'section_results': section_results,
        'total_score': total_score,  # Total score in marks
        'total_questions': total_questions,
        'max_possible_marks': max_possible_marks,
        'overall_percentage': round(overall_percentage, 1),
        'time_taken': time_taken,
        'recommended_books': recommended_books
    })

def super_quiz_solutions(request, quiz_id):
    """Display all questions with correct answers and explanations for a super quiz"""
    quiz = get_object_or_404(SuperQuiz, quiz_id=quiz_id)
    question_sets = SuperQuestionSet.objects.filter(quiz_id=quiz_id).order_by('part_number')
    sections = []
    for qs in question_sets:
        part_name = quiz.part_names.get(str(qs.part_number), f"Part {qs.part_number}")
        solutions = []
        for i, q in enumerate(qs.questions):
            solutions.append({
                'question': q['question'],
                'options': q['options'],
                'correct_answer': q['answer'],
                'explanation': q.get('explanation', ''),
            })
        sections.append({
            'part_number': qs.part_number,
            'part_name': part_name,
            'solutions': solutions,
            'total': len(qs.questions),
        })

    recommended_books = RecommendedBook.objects.order_by('?')[:7]

    return render(request, 'quiz/super_quiz_solutions.html', {
        'quiz': quiz,
        'sections': sections,
        'recommended_books': recommended_books
    })

class HttpResponseTooManyRequests(HttpResponse):
    status_code = 429

def conditional_login_required(view_func):
    """Decorator that requires login only if the quiz requires signup"""

    @wraps(view_func)
    def _wrapped_view(request, quiz_id, *args, **kwargs):
        quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
        if quiz.requires_signup and not request.user.is_authenticated:
            messages.info(request, 'Please sign in to take this quiz.')
            return redirect('account_login')
        return view_func(request, quiz_id, *args, **kwargs)

    return _wrapped_view

@login_required
@require_http_methods(["POST"])
@ratelimit(key='ip', rate='30/m', block=True)
def like_blog_post(request, post_id):
    if getattr(request, 'limited', False):
        return HttpResponseTooManyRequests("Too many requests. Please slow down.")

    blog_post = get_object_or_404(BlogPost, post_id=post_id)
    user = request.user

    # Toggle like
    if user in blog_post.likes.all():
        blog_post.likes.remove(user)
        liked = False
    else:
        blog_post.likes.add(user)
        liked = True

    return JsonResponse({
        'status': 'success',
        'liked': liked,
        'like_count': blog_post.like_count(),
    })

def Send_report_telegram(user_message):
    import requests
    BOT_TOKEN = ''
    CHAT_ID = ''

    MESSAGE = str(user_message)

    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': CHAT_ID,
        'text': MESSAGE
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print('Message sent successfully!')
    else:
        print(f'Failed to send message: {response.text}')

@login_required
@require_http_methods(["POST"])
@ratelimit(key='ip', rate='30/d', block=True)
def report_issue(request, quiz_id):
    if getattr(request, 'limited', False):
        return HttpResponseTooManyRequests("Too many requests. Please slow down.")

    data = json.loads(request.body.decode("utf-8"))
    issue_text = data.get('issue', '').strip()
    question_index = data.get('question_index', None)
    quiz_type = data.get('quiz_type', None)

    user = request.user.username
    message = f"""
Type: {quiz_type}
Quiz ID: {quiz_id}
Question Index: {question_index}
Issue: {issue_text}
User:{user}
"""
    Send_report_telegram(message)
    return JsonResponse({'status': 'success', 'message': 'Issue sent successfully.'})



def blog_list(request):
    """Display a list of blog posts."""
    page = request.GET.get('page', 1)
    posts = BlogPost.objects.all()
    paginator = Paginator(posts, 5)
    page_obj = paginator.get_page(page)

    return render(request, 'quiz/blog_list.html', {
        'page_obj': page_obj,
    })

def blog_detail(request, post_id):
    """Display a single blog post."""
    post = get_object_or_404(BlogPost, post_id=post_id)
    recommended_books = RecommendedBook.objects.order_by('?')[:3]

    return render(request, 'quiz/blog_detail.html', {
        'post': post,
        'recommended_books': recommended_books
    })

def accept_terms(request):
    user_id = request.session.get('pending_social_user_id')
    if not user_id:
        return redirect('account_login')

    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('account_login')

    if request.method == "POST":
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.terms_accepted_at = timezone.now()
        profile.save()
        # Log the user in
        from django.contrib.auth import login
        login(request, user)
        del request.session['pending_social_user_id']
        return redirect('/')

    return render(request, 'account/accept_terms.html', {'user': user})


# quiz/views.py
def home(request):
    # quizzes = Quiz.objects.order_by('-quiz_id')[:6]
    # advance_quizzes = AdvanceQuiz.objects.order_by('-quiz_id')[:3]
    # super_quizzes = SuperQuiz.objects.order_by('-quiz_id')[:3]
    # blog_posts = BlogPost.objects.order_by('-post_id')[:3]

    quizzes = Quiz.objects.order_by('?')[:6]
    advance_quizzes = AdvanceQuiz.objects.order_by('?')[:6]
    super_quizzes = SuperQuiz.objects.order_by('?')[:3]
    blog_posts = BlogPost.objects.order_by('?')[:3]

    if request.user.is_authenticated:
        quizzes = quizzes.annotate(
            has_attempted=Exists(
                QuizAttempt.objects.filter(
                    user=request.user,
                    quiz_id=OuterRef('quiz_id')
                )
            )
        )
        advance_quizzes = advance_quizzes.annotate(
            has_attempted=Exists(
                AdvanceQuizAttempt.objects.filter(
                    user=request.user,
                    quiz_id=OuterRef('quiz_id')
                )
            )
        )
        super_quizzes = super_quizzes.annotate(
            has_attempted=Exists(
                SuperQuizAttempt.objects.filter(
                    user=request.user,
                    quiz_id=OuterRef('quiz_id')
                )
            )
        )
        blog_posts = blog_posts.annotate(
            has_liked=Exists(
                BlogPost.likes.through.objects.filter(
                    user=request.user,
                    blogpost_id=OuterRef('post_id')
                )
            )
        )
    else:
        quizzes = quizzes.annotate(has_attempted=Value(False, output_field=BooleanField()))
        advance_quizzes = advance_quizzes.annotate(has_attempted=Value(False, output_field=BooleanField()))
        super_quizzes = super_quizzes.annotate(has_attempted=Value(False, output_field=BooleanField()))
        blog_posts = blog_posts.annotate(has_liked=Value(False, output_field=BooleanField()))

    return render(request, 'quiz/home.html', {
        'quizzes': quizzes,
        'advance_quizzes': advance_quizzes,
        'super_quizzes': super_quizzes,
        'blog_posts': blog_posts,
    })

def quiz_solutions(request, quiz_id):
    """Display all questions with correct answers and explanations for a quiz."""
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    question_set = get_object_or_404(QuestionSet, quiz_id=quiz_id)
    questions = question_set.questions

    # Prepare data for the template
    solutions = []
    for i, q in enumerate(questions):
        solutions.append({
            'question': q['question'],
            'options': q['options'],
            'correct_answer': q['answer'],
            'explanation': q.get('explanation', ''),
        })

    recommended_books = RecommendedBook.objects.order_by('?')[:7]

    context = {
        'quiz': quiz,
        'solutions': solutions,
        'total': len(questions),
        'recommended_books': recommended_books
    }

    return render(request, 'quiz/solutions.html', context)


@ratelimit(key='ip', rate='30/m', block=True)
def search_quizzes(request):
    if getattr(request, 'limited', False):
        return HttpResponseTooManyRequests("Too many requests. Please slow down.")

    query = request.GET.get('q', '')
    tag = request.GET.get('tag', '')
    page = request.GET.get('page', 1)
    quiz_type = request.GET.get('quiz_type', '')

    if quiz_type == 'super':
        quizzes = SuperQuiz.objects.all()
        if query:
            quizzes = quizzes.filter(
                Q(quiz_name__icontains=query) |
                Q(exam_tags__icontains=query)
            )
        if tag:
            quizzes = quizzes.filter(exam_tags__contains=[tag.strip()])
        if request.user.is_authenticated:
            quizzes = quizzes.annotate(
                has_attempted=Exists(
                    SuperQuizAttempt.objects.filter(
                        user=request.user,
                        quiz_id=OuterRef('quiz_id')
                    )
                )
            )
        else:
            # quizzes = quizzes.annotate(has_attempted=Value(False, output_field=BooleanField()))
            pass

    elif quiz_type == 'advance':
        quizzes = AdvanceQuiz.objects.all()
        if query:
            quizzes = quizzes.filter(
                Q(quiz_name__icontains=query) |
                Q(exam_tags__icontains=query)
            )
        if tag:
            quizzes = quizzes.filter(exam_tags__contains=[tag.strip()])
        if request.user.is_authenticated:
            quizzes = quizzes.annotate(
                has_attempted=Exists(
                    AdvanceQuizAttempt.objects.filter(
                        user=request.user,
                        quiz_id=OuterRef('quiz_id')
                    )
                )
            )
        else:
            # quizzes = quizzes.annotate(has_attempted=Value(False, output_field=BooleanField()))
            pass

    else:
        quizzes = Quiz.objects.all()

        if query:
            quizzes = quizzes.filter(
                Q(quiz_name__icontains=query) |
                Q(exam_tags__icontains=query)
            )

        if tag:
            quizzes = quizzes.filter(exam_tags__contains=[tag.strip()])

        # Annotate quizzes with whether the user has attempted them
        if request.user.is_authenticated:
            quizzes = quizzes.annotate(
                has_attempted=Exists(
                    QuizAttempt.objects.filter(
                        user=request.user,
                        quiz_id=OuterRef('quiz_id')
                    )
                )
            )
        else:
            pass

    quizzes = quizzes.order_by('-quiz_id')
    paginator = Paginator(quizzes, 15)
    page_obj = paginator.get_page(page)

    if quiz_type == 'super':
        tags = get_all_tags(SuperQuiz)
    elif quiz_type == 'advance':
        tags = get_all_tags(AdvanceQuiz)
    else:
        tags = get_all_tags(Quiz)

    return render(request, 'quiz/search.html', {
        'quiz_type': quiz_type,
        'page_obj': page_obj,
        'query': query,
        'tag': tag,
        'tags': tags,
    })

# quiz/views.py

def quiz_list_partial(request):
    query = request.GET.get('q', '')
    tag = request.GET.get('tag', '')
    page = request.GET.get('page', 1)
    quiz_type = request.GET.get('quiz_type', '')  # Add quiz_type parameter

    if quiz_type == 'super':
        quizzes = SuperQuiz.objects.all()
        template_name = 'quiz/partials/quiz_cards.html'  # Reuse or create specific template if needed
        if query:
            quizzes = quizzes.filter(
                Q(quiz_name__icontains=query) |
                Q(exam_tags__icontains=query)
            )
        if tag:
            quizzes = quizzes.filter(exam_tags__contains=[tag.strip()])
        if request.user.is_authenticated:
            quizzes = quizzes.annotate(
                has_attempted=Exists(
                    SuperQuizAttempt.objects.filter(
                        user=request.user,
                        quiz_id=OuterRef('quiz_id')
                    )
                )
            )
    elif quiz_type == 'advance':
        quizzes = AdvanceQuiz.objects.all()
        template_name = 'quiz/partials/quiz_cards.html'  # Reuse or create specific template if needed
        if query:
            quizzes = quizzes.filter(
                Q(quiz_name__icontains=query) |
                Q(exam_tags__icontains=query)
            )
        if tag:
            quizzes = quizzes.filter(exam_tags__contains=[tag.strip()])
        if request.user.is_authenticated:
            quizzes = quizzes.annotate(
                has_attempted=Exists(
                    AdvanceQuizAttempt.objects.filter(
                        user=request.user,
                        quiz_id=OuterRef('quiz_id')
                    )
                )
            )
    else:
        quizzes = Quiz.objects.all()
        template_name = 'quiz/partials/quiz_cards.html'
        if query:
            quizzes = quizzes.filter(
                Q(quiz_name__icontains=query) |
                Q(exam_tags__icontains=query)
            )
        if tag:
            quizzes = quizzes.filter(exam_tags__contains=[tag.strip()])
        if request.user.is_authenticated:
            quizzes = quizzes.annotate(
                has_attempted=Exists(
                    QuizAttempt.objects.filter(
                        user=request.user,
                        quiz_id=OuterRef('quiz_id')
                    )
                )
            )

    quizzes = quizzes.order_by('-quiz_id')
    paginator = Paginator(quizzes, 15)
    page_obj = paginator.get_page(page)

    return render(request, template_name, {
        'page_obj': page_obj,
        'query': query,
        'tag': tag,
        'quiz_type': quiz_type,  # Pass quiz_type to template
    })

def get_all_tags(quiz_model=None):
    """Extract unique tags from quizzes, optionally filtered by quiz model"""
    if quiz_model is None:
        quiz_model = Quiz  # default to normal quiz

    all_tags = quiz_model.objects.values_list('exam_tags', flat=True)
    tag_set = set()
    for taglist in all_tags:
        if taglist:
            tag_set.update(taglist)
    return sorted(tag_set)



def quiz_detail(request, quiz_id):
    """Quiz detail page with start quiz functionality"""
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)

    # Check if quiz requires signup and user is not authenticated
    if quiz.requires_signup and not request.user.is_authenticated:
        messages.info(request, 'Please sign in to take this quiz.')
        return redirect('account_login')

    if request.method == 'POST' or request.htmx:
        # Initialize session for quiz answers
        user_id = request.user.id if request.user.is_authenticated else 'anonymous'
        session_key = f'{quiz_id}_answers_{user_id}'
        request.session[session_key] = {}
        if request.htmx:
            return HttpResponseClientRedirect(
                reverse('question', kwargs={'quiz_id': quiz_id, 'question_index': 0})
            )
        return redirect('question', quiz_id=quiz_id, question_index=0)
    # Render quiz detail page for GET requests
    return render(request, 'quiz/quiz_detail.html', {'quiz': quiz})


@conditional_login_required
def start_quiz(request, quiz_id):
    """Start a quiz by redirecting to first question"""
    user_id = request.user.id if request.user.is_authenticated else 'anonymous'
    session_key = f'{quiz_id}_answers_{user_id}'
    request.session[session_key] = {}
    messages.success(request, f'Quiz started! Good luck!')
    return redirect('question', quiz_id=quiz_id, question_index=0)


# quiz_result (unchanged, included for context)
@ratelimit(key='ip', rate='30/m', block=True)
@conditional_login_required
def quiz_result(request, quiz_id):
    """Display quiz results and save attempt"""

    if getattr(request, 'limited', False):
        return HttpResponseTooManyRequests("Too many requests. Please slow down.")

    question_set = get_object_or_404(QuestionSet, quiz_id=quiz_id)
    questions = question_set.questions
    user_id = request.user.id if request.user.is_authenticated else 'anonymous'
    session_key = f'{quiz_id}_answers_{user_id}'
    answers = request.session.get(session_key, {})

    if not answers:
        messages.error(request, 'No quiz answers found. Please start the quiz again.')
        return redirect('start_quiz', quiz_id=quiz_id)

    score = 0
    results = []
    for i, q in enumerate(questions):
        correct = q['answer']
        user_ans = answers.get(str(i), '')
        is_correct = user_ans == correct
        if is_correct:
            score += 1
        results.append({
            'question': q['question'],
            'options': q['options'],
            'your_answer': user_ans,
            'correct_answer': correct,
            'is_correct': is_correct,
            'explanation': q.get('explanation', '')
        })

    percentage = (score / len(questions)) * 100 if questions else 0

    if request.user.is_authenticated:
        UserProfile.objects.get_or_create(user=request.user)
        QuizAttempt.objects.create(
            user=request.user,
            quiz=get_object_or_404(Quiz, quiz_id=quiz_id),
            score=score,
            total_questions=len(questions),
            percentage=percentage,
            answers=answers
        )

    if session_key in request.session:
        del request.session[session_key]
        request.session.modified = True

    context = {
        'quiz': get_object_or_404(Quiz, quiz_id=quiz_id),
        'score': score,
        'total': len(questions),
        'percentage': round(percentage, 1),
        'results': results,
        'user': request.user,
    }

    if request.htmx:
        return render(request, 'quiz/partials/result_content.html', context)
    return render(request, 'quiz/result.html', context)

@login_required
def user_profile(request):
    user = request.user
    UserProfile.objects.get_or_create(user=user)

    # Fetch attempts for all quiz types
    quiz_attempts = QuizAttempt.objects.filter(user=user).select_related('quiz').order_by('-attempt_date')
    super_quiz_attempts = SuperQuizAttempt.objects.filter(user=user).select_related('quiz').order_by('-attempt_date')
    advance_quiz_attempts = AdvanceQuizAttempt.objects.filter(user=user).select_related('quiz').order_by('-attempt_date')

    # Paginate each queryset
    quizzes_per_page = 9
    quiz_paginator = Paginator(quiz_attempts, quizzes_per_page)
    super_quiz_paginator = Paginator(super_quiz_attempts, quizzes_per_page)
    advance_quiz_paginator = Paginator(advance_quiz_attempts, quizzes_per_page)

    # Get page numbers from request
    quiz_page = request.GET.get('quiz_page', 1)
    super_quiz_page = request.GET.get('super_quiz_page', 1)
    advance_quiz_page = request.GET.get('advance_quiz_page', 1)

    # Get paginated objects
    quiz_page_obj = quiz_paginator.get_page(quiz_page)
    super_quiz_page_obj = super_quiz_paginator.get_page(super_quiz_page)
    advance_quiz_page_obj = advance_quiz_paginator.get_page(advance_quiz_page)

    context = {
        'quiz_page_obj': quiz_page_obj,
        'super_quiz_page_obj': super_quiz_page_obj,
        'advance_quiz_page_obj': advance_quiz_page_obj,
        'edit_mode': request.GET.get('edit') == 'true' or request.method == 'POST',
    }
    return render(request, 'quiz/profile.html', context)

@conditional_login_required
def quiz_paginated(request, quiz_id):
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    question_set = get_object_or_404(QuestionSet, quiz_id=quiz_id)
    return render(request, 'quiz/quiz_paginated.html', {
        'quiz': quiz,
        'questions': question_set.questions,
    })


@conditional_login_required
@require_http_methods(["POST"])
@ratelimit(key='ip', rate='30/m', block=True)
def quiz_submit_paginated(request, quiz_id):
    if getattr(request, 'limited', False):
        return HttpResponseTooManyRequests("Too many requests. Please slow down.")

    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    question_set = get_object_or_404(QuestionSet, quiz_id=quiz_id)
    questions = question_set.questions

    try:
        answers = json.loads(request.POST.get('answers', '{}'))
        time_taken = int(request.POST.get('time_taken', 0))  # Get time_taken from POST
    except (json.JSONDecodeError, ValueError):
        messages.error(request, "Invalid answers submitted.")
        return redirect('quiz_paginated', quiz_id=quiz_id)

    score = 0
    results = []

    for i, q in enumerate(questions):
        user_ans = answers.get(str(i), '')
        correct = q['answer']
        is_correct = user_ans == correct
        if is_correct:
            score += 1
        results.append({
            'question': q['question'],
            'options': q['options'],
            'your_answer': user_ans,
            'correct_answer': correct,
            'is_correct': is_correct,
            'explanation': q.get('explanation', '')
        })

    percentage = (score / len(questions)) * 100 if questions else 0

    if request.user.is_authenticated:
        UserProfile.objects.get_or_create(user=request.user)
        QuizAttempt.objects.update_or_create(
            user=request.user,
            quiz=quiz,
            defaults={
                'score': score,
                'total_questions': len(questions),
                'percentage': percentage,
                'answers': answers,
                'attempt_date': timezone.now(),
                'total_score': 10
            }
        )

    recommended_books = RecommendedBook.objects.order_by('?')[:7]

    return render(request, 'quiz/result.html', {
        'quiz': quiz,
        'score': score,
        'total': len(questions),
        'percentage': round(percentage, 1),
        'results': results,
        'time_taken': time_taken,  # Pass time_taken to template
        'recommended_books': recommended_books
    })
