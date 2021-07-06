from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Post, Comment
from .forms import PostForm, CommentForm

from django.views.generic import (TemplateView,ListView,
                                  DetailView,CreateView,
                                  UpdateView,DeleteView)

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class AboutView(TemplateView):
    template_name = 'blog/about.html'


class PostListView(ListView):
    model = Post

    # This works like SQL query, but just python verion
    # We grab all the objects/posts from Post and filter out the conditions written in the following
    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')

class PostDetailView(DetailView):
    model = Post

# LoginRequiredMixin make sure only users can create, update, or delete the post
class CreatePostView(LoginRequiredMixin,CreateView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'

    form_class = PostForm

    model = Post


class PostUpdateView(LoginRequiredMixin,UpdateView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'

    form_class = PostForm

    model = Post


class PostDeleteView(LoginRequiredMixin,DeleteView):
    model = Post
    # reverse_lazy will make sure we go back to post_list after we successfully delete the post
    success_url = reverse_lazy('post_list')


class DraftListView(LoginRequiredMixin,ListView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_draft_list.html'

    model = Post

    # Grab all the objects/drafts that don't have a published date since every draft shouldn't have a published date
    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by('created_date')


#######################################
## Functions that require a pk match ##
#######################################

# This decorator make sure users have to log in in order to post a comment
@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)

@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/comment_form.html', {'form': form})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    # Have to save the primary key to a variable because after we delete the comment, there is no more comment object, but we still need to redirect to the post_detail page
    post_pk = comment.post.pk
    comment.delete()
    return redirect('post_detail', pk=post_pk)
