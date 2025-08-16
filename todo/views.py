from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Todo
from .forms import TodoForm, UserRegistrationForm
from django.utils import timezone

def home(request):
    """Home view with todo statistics and quick actions"""
    if request.user.is_authenticated:
        total_todos = Todo.objects.filter(user=request.user).count()
        pending_todos = Todo.objects.filter(user=request.user, status='pending').count()
        completed_todos = Todo.objects.filter(user=request.user, status='completed').count()
        overdue_todos = Todo.objects.filter(user=request.user, status='pending').filter(due_date__lt=timezone.now()).count()
        
        context = {
            'total_todos': total_todos,
            'pending_todos': pending_todos,
            'completed_todos': completed_todos,
            'overdue_todos': overdue_todos,
            'recent_todos': Todo.objects.filter(user=request.user)[:5],
        }
    else:
        context = {}
    return render(request, 'todo/home.html', context)

def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('todo:home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('todo:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'todo/register.html', {'form': form})

def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('todo:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('todo:home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'todo/login.html')

def user_logout(request):
    """Custom logout view that handles GET requests"""
    logout(request)
    messages.success(request, 'You have been successfully logged out!')
    return redirect('todo:home')

class TodoListView(LoginRequiredMixin, ListView):
    model = Todo
    template_name = 'todo/todo_list.html'
    context_object_name = 'todos'
    paginate_by = 10
    login_url = 'todo:login'
    
    def get_queryset(self):
        queryset = Todo.objects.filter(user=self.request.user)
        status_filter = self.request.GET.get('status')
        priority_filter = self.request.GET.get('priority')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Todo.STATUS_CHOICES
        context['priority_choices'] = Todo.PRIORITY_CHOICES
        return context

class TodoCreateView(LoginRequiredMixin, CreateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todo/todo_form.html'
    success_url = reverse_lazy('todo:todo_list')
    login_url = 'todo:login'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Task created successfully!')
        return super().form_valid(form)

class TodoUpdateView(LoginRequiredMixin, UpdateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todo/todo_form.html'
    success_url = reverse_lazy('todo:todo_list')
    login_url = 'todo:login'
    
    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Task updated successfully!')
        return super().form_valid(form)

class TodoDeleteView(LoginRequiredMixin, DeleteView):
    model = Todo
    template_name = 'todo/todo_confirm_delete.html'
    success_url = reverse_lazy('todo:todo_list')
    login_url = 'todo:login'
    
    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Task deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required(login_url='todo:login')
def toggle_status(request, pk):
    """Toggle todo status between pending and completed"""
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    if todo.status == 'pending':
        todo.status = 'completed'
        messages.success(request, f'Task "{todo.title}" marked as completed!')
    else:
        todo.status = 'pending'
        messages.info(request, f'Task "{todo.title}" marked as pending!')
    todo.save()
    return redirect('todo:todo_list')

@login_required(login_url='todo:login')
def quick_add(request):
    """Quick add a simple todo without full form"""
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            Todo.objects.create(
                user=request.user,
                title=title
            )
            messages.success(request, 'Quick task added successfully!')
        else:
            messages.error(request, 'Task title is required!')
    return redirect('todo:todo_list')
