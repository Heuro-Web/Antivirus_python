from apps.exams.models import Exam, Question, Choice


def run():
    exam, _ = Exam.objects.get_or_create(title='Programmation sécurisée', defaults={'duration_minutes': 45})
    q1, _ = Question.objects.get_or_create(exam=exam, prompt='Quel header bloque le clickjacking ?', question_type='mcq')
    Choice.objects.get_or_create(question=q1, text='X-Frame-Options', is_correct=True)
    Choice.objects.get_or_create(question=q1, text='X-Powered-By', is_correct=False)
    Question.objects.get_or_create(exam=exam, prompt='Définir CSRF.', question_type='short', expected_answer='cross-site request forgery')
    print('Seed terminé')
