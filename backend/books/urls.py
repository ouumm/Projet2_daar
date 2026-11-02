from django.urls import path

from . import views

urlpatterns = [
    path("books/", views.BookList.as_view()),
    path("book/<int:pk>/", views.BookDetail.as_view()),
    path("book/<int:pk>/click/", views.BookClick.as_view()),
    path("book/<int:pk>/text/", views.BookText.as_view()),
]
