from django.urls import path
from . import views

app_name = 'todo'

urlpatterns = [
    path('', views.home, name='home'),
    
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Todo URLs (require authentication)
    path('todos/', views.TodoListView.as_view(), name='todo_list'),
    path('todos/create/', views.TodoCreateView.as_view(), name='todo_create'),
    path('todos/<int:pk>/update/', views.TodoUpdateView.as_view(), name='todo_update'),
    path('todos/<int:pk>/delete/', views.TodoDeleteView.as_view(), name='todo_delete'),
    path('todos/<int:pk>/toggle/', views.toggle_status, name='toggle_status'),
    path('quick-add/', views.quick_add, name='quick_add'),
]
