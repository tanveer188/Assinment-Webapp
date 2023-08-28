from django.contrib.auth.models import User
from django.db import models
from django.utils.html import escape, mark_safe
from authentication.models import TeacherModel,SubjectModel
from django.db.models import Count, Sum
from django.db.models.functions import Concat
from decimal import Decimal
# class Subject(models.Model):
#     name = models.CharField(max_length=30)
#     color = models.CharField(max_length=7, default='#007bff')

#     def __str__(self):
#         return self.name

#     def get_html_badge(self):
#         name = escape(self.name)
#         color = escape(self.color)
#         html = '<span class="badge badge-primary" style="background-color: %s">%s</span>' % (color, name)
#         return mark_safe(html)


class Quiz(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    name = models.CharField(max_length=255)
    subject = models.ForeignKey(SubjectModel, on_delete=models.CASCADE, related_name='quizzes')
    is_done = models.BooleanField(default=False)
    avg_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))

    def are_all_questions_quiz(self):
        return self.questions.filter(question_type='quiz').count() == self.questions.count()

    def update_avg_score(self):
        taken_quizzes = self.taken_quizzes.filter(is_checked=True)
        total_taken_quizzes = taken_quizzes.count()

        if total_taken_quizzes > 0:
            total_scores = taken_quizzes.aggregate(total=Sum('score'))['total']
            avg_score = total_scores / total_taken_quizzes
            self.avg_score = round(avg_score, 2)
        else:
            self.avg_score = Decimal('0.00')

        self.save()

    def __str__(self):
        return self.name

class Question(models.Model):
    QUESTION_TYPE_CHOICES = (
        ('justification', 'Justification'),
        ('quiz', 'Quiz'),
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField('Question')
    question_type = models.CharField(max_length=15, choices=QUESTION_TYPE_CHOICES)

    def __str__(self):
        return str(self.quiz.name)+" : "+str(self.text)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField('Answer', max_length=255)
    is_correct = models.BooleanField('Correct answer', default=False)

    def __str__(self):
        return str(self.text)

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    quizzes = models.ManyToManyField(Quiz, through='TakenQuiz')
    score = models.IntegerField(default=0)
    def update_score(self):
        self.score = self.taken_quizzes.aggregate(Sum('score'))['score__sum'] or 0
        self.save()

    def get_unanswered_questions(self, quiz):
        answered_questions = list(
            self.quiz_answers.values_list('question__pk', flat=True)
        ) + list(
            self.justification_answer.values_list('question__pk', flat=True)
        )
        questions = quiz.questions.exclude(pk__in=answered_questions).order_by('text')
        return questions
    def get_justification_questions(self,quiz):
      answered_questions = self.justification_answer.filter(score=None).values_list('question__pk', flat=True)
      questions = quiz.questions.filter(pk__in=answered_questions).order_by("text")
      return questions
    def __str__(self):
        return self.user.username

class TakenQuiz(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='taken_quizzes')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='taken_quizzes')
    date = models.DateTimeField(auto_now_add=True)
    is_checked = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))

    def calculate_score_and_percentage(self):
        total_questions = self.quiz.questions.count()

        correct_quiz_answers = self.student.quiz_answers.filter(
            answer__question__quiz=self.quiz,
            answer__is_correct=True
        ).count()

        justification_answers = self.student.justification_answer.filter(
            question__quiz=self.quiz,
            score__isnull=False
        ).count()
        
        correct_answers = correct_quiz_answers + justification_answers
        # Calculate the score using .aggregate() and extract the sum
        score_result = self.student.justification_answer.filter(
            question__quiz=self.quiz,
            score__isnull=False
        ).aggregate(Sum("score"))
        
        # Extract the sum from the dictionary using the key
        score_sum = score_result['score__sum']
        
        # If score_sum is None, set it to 0
        if score_sum is None:
            score_sum = 0
        
        self.score = correct_answers + score_sum
        self.percentage = (correct_answers / total_questions) * 100
        self.save()
        self.quiz.update_avg_score()


class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score = models.IntegerField(blank=True,null=True)
    question = models.ForeignKey("Question",on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.student.user.username} - {self.answer}"

class StudentQuizAnswer(StudentAnswer):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='quiz_answers')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='+')

    def __str__(self):
        return f"{self.student.user.username} - {self.answer.text} (Quiz Answer)"

class StudentJustificationAnswer(StudentAnswer):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='justification_answer')
    answer = models.TextField("Answer")

    def __str__(self):
        return f"{self.student.user.username} - {self.answer} (Justification Answer)"


class Trait(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class TraitRating(models.Model):
    trait = models.ForeignKey(Trait, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(6)])  # Rating value from 0 to 5

    def __str__(self):
        return f"{self.trait.name} - {self.student.user.username}"


class WebsiteVisit(models.Model):
    ip_address = models.GenericIPAddressField()
    visit_date = models.DateField()
    visit_time = models.TimeField()
    url_name = models.CharField(max_length=255)
    visited_url = models.URLField()

    def __str__(self):
        return f"{self.ip_address} - {self.visit_date} {self.visit_time} - {self.url_name}"

