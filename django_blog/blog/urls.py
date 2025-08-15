from django.urls import path 
from django.contrib.auth import views
from .views import (CustomLoginView, CustomLogoutView, RegisterView, ListPostView, CreatePostView, UpdatePostView, CommentDetailView,
                    DetailPostView, DeletePostView, CommentDeleteView, CommentCreateView, CommentUpdateView, PostByTagListView, 
                    profile, search_posts)




urlpatterns = [
    #inbuilt auth views
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name= 'logout'),

    # Custom user views
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', profile, name='profile'),

    #Custom Post views
    path('posts/', ListPostView.as_view(), name='home'),
    path('post/<int:pk>/', DetailPostView.as_view(), name='post_detail'),
    path('post/new/', CreatePostView.as_view(), name='post_create'),
    path('post/<int:pk>/update/', UpdatePostView.as_view(), name='post_update'),
    path('post/<int:pk>/delete/', DeletePostView.as_view(), name='post_delete'),

    #Custom Comment views
    path('post/<int:pk>/comments/new/', CommentCreateView.as_view(), name='comment_create'),
    path('comment/<int:pk>/update/', CommentUpdateView.as_view(), name='comment_edit'),
    path('comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment_delete'),
    path('comment/<int:pk>/', CommentDetailView.as_view(), name='comment_detail'),

    #tags views
    path('tags/<slug:tag_slug>/', PostByTagListView.as_view(), name='posts_by_tag'),
    path('search/', search_posts, name='search_posts'),
]
