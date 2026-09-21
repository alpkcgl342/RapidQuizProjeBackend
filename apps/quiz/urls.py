from django.urls import path

from . import views

urlpatterns = [
    path("quiz-sessions/", views.QuizSessionCreateView.as_view(), name="session-create"),
    path(
        "quiz-sessions/<uuid:pk>/current-question/",
        views.CurrentQuestionView.as_view(),
        name="session-current-question",
    ),
    path("quiz-sessions/<uuid:pk>/answers/", views.AnswerView.as_view(), name="session-answers"),
    path("quiz-sessions/<uuid:pk>/summary/", views.SummaryView.as_view(), name="session-summary"),
    path(
        "quiz-sessions/<uuid:pk>/submit-score/",
        views.SubmitScoreView.as_view(),
        name="session-submit-score",
    ),
]
