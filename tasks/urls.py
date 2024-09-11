from django.urls import path

from tasks import views

urlpatterns = [
    path("tasks/", views.TasksListAPIView.as_view()),
    path("tasks/<pk>", views.TaskDetailAPIView.as_view()),
]
