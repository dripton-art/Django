from .models import Post, Comment
from .forms import CustomUserCreationForm, ProfileEditForm, PostCreationForm, CommentForm
from .serializers import PostSerializer
from .permissions import IsAuthorOrReadOnly

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages

from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse

from django.views import View
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView
from django.views.generic.edit import FormMixin

from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from taggit.models import Tag
from django.db.models import Q


# Create your views here.

#Registeration views for users
class RegisterView(View):
    '''get form from forms.py'''
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request,'blog/register.html', {'form':form} )
    '''save form to database'''
    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
        return render(request, 'blog/register.html', {'form': form})

#views to view and edit profile. 
@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance = request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated")
            return redirect('profile')
    else:
        form = ProfileEditForm(instance = request.user)
    return render(request, 'blog/profile.html', {'form': form})


# Login & Logout (using Django's built-in views)
class CustomLoginView(LoginView):
    template_name = 'blog/login.html'

class CustomLogoutView(LogoutView):
    template_name = 'blog/logout.html'

# --- POST VIEWS (API CRUD) ---

# ListView to display all blog posts.
class PostListView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

# DetailView to show individual blog posts.
class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

# CreateView to allow authenticated users to create new posts.
class PostCreateView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

# UpdateView to enable post authors to edit their posts.
class PostUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

# DeleteView to let authors delete their posts.
class PostDeleteView(generics.RetrieveDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]


# --- POST VIEWS (HTML CRUD) ---

# List all posts
class ListPostView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    ordering = ['published_date']


# View single post details
class DetailPostView(FormMixin, DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    form_class = CommentForm

    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['comments'] = self.object.comments.all()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = self.request.user
            comment.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)



#create a new post only user is logged in
class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostCreationForm
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('home')  # Redirect after success

    def form_valid(self, form):
        # Set the author to the logged-in user before saving
        form.instance.author = self.request.user
        return super().form_valid(form)

class UpdatePostView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostCreationForm
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        """Allow only the author to update their post."""
        post = self.get_object()
        return post.author == self.request.user
    
# Delete a post (only author allowed)
class DeletePostView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user


# --- Commment Views(CRUD) ---
# View for details of comment
class CommentDetailView(DetailView):
    queryset = Comment.objects.all()
    template_name = 'blog/comment_detail.html'
    context_obj_name = 'comment'

# views to Create comment
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['content']  # whatever fields your Comment model has

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.kwargs['pk']})


# Update Comment (only author)
class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment_form.html'

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user

    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.object.post.pk})
    
# Delete Comment (only author)
class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment_delete.html'

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user

    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.object.post.pk})
    


# def posts_by_tag(request, tag_slug):
#     tag = get_object_or_404(Tag, slug= tag_slug)
#     posts = Post.objects.filter(tags__in=[tag])
#     return render(request, 'blog/posts_by_tag.html', {'tag': tag, 'posts': posts})

class PostByTagListView(ListView):
    model = Post
    template_name = 'blog/posts_by_tag.html'
    context_object_name = 'posts'

    def get_queryset(self):
        tag_slug = self.kwargs.get('tag_slug')
        self.tag = get_object_or_404(Tag, slug=tag_slug)
        return Post.objects.filter(tags__slug=tag_slug).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context    

# Search views for the comments and post
def search_posts(request):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        results = Post.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__name__icontains=query)  # works with django-taggit
        ).distinct()

    return render(request, 'blog/search_results.html', {
        'query': query,
        'results': results
    })

