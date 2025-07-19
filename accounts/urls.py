from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView, index, RegisterView, UserListView, UserUpdateView, UserDeleteView,leadership, admissions, gallery, departments

urlpatterns = [
    path('', index, name='index'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='analytics'), name='logout'), 
    path('register/', RegisterView.as_view(), name='register'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),

    path('departments/', departments, name='departments'),
    path('leadership/', leadership, name='leadership'),
    path('admissions/', admissions, name='admissions'),
    path('gallery/', gallery, name='gallery'),
]