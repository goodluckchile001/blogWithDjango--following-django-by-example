from django.core.mail import send_mail
from django.db.models import Count
from django.shortcuts import render, get_object_or_404

from .models import Post
from django.views.generic import FormView, ListView, DetailView,View
from .forms import EmailPostForm, CommentForm
from taggit.models import Tag


class PostComment(View):
    template_name = 'blog/post/comment.html'
    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(
            Post, id=self.kwargs.get("post_id"), status=Post.Status.PUBLISHED
        )
        return super().dispatch(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        comment = None 
        form = CommentForm(data=request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.post_obj
            comment.save()
    
        return render(
            request,
            self.template_name,  # Use the class attribute
            {'post': self.post_obj, 'form': form, 'comment': comment}
        )



class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 4
    template_name = 'blog/post/list.html'

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context

    
    def get_queryset(self):
        qs = super().get_queryset()
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug :
            self.tag = get_object_or_404(Tag,slug=tag_slug)
            return qs.filter(tags__in=[self.tag])
        
        self.tag=None
        return qs
    


    
class PostShareView(FormView):
    form_class = EmailPostForm
    template_name = 'blog/post/share.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(
            Post,id=self.kwargs.get("post_id"),status=Post.Status.PUBLISHED
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.post_obj
        context['sent'] = kwargs.get('sent',False)
        return context

    def form_valid(self,form):
        cd = form.cleaned_data
        post_url = self.request.build_absolute_uri(
            self.post_obj.get_absolute_url()
        ) 
        subject = f"{cd['name']} ({cd['email']}) recommends you read {self.post_obj.title}"
        message = f"Read {self.post_obj.title} at {post_url}\n\n{cd['name']}\'s comments:{cd['comments']}"
        send_mail(subject, message, None, [cd['to']])
        return self.render_to_response(self.get_context_data(form=form,sent=True))


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post/detail.html"
    context_object_name = 'post'
    
    

    def get_object(self, queryset=None):
        return get_object_or_404(
            Post,
            status=Post.Status.PUBLISHED,
            slug=self.kwargs.get("post"),
            publish__year=self.kwargs.get("year"),
            publish__month=self.kwargs.get("month"),
            publish__day=self.kwargs.get("day"),

    
        )
        
    def get_context_data(self, **kwargs):
        similar_posts = Post.published.filter(tags__in=self.object.tags.values_list("id", flat=True))
        similar_posts = similar_posts.exclude(id=self.object.id).distinct()
        similar_posts = similar_posts.annotate(same_tags=Count("tags")).order_by("-same_tags","-publish")[:4]


        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context["post_tag_ids"]= self.object.tags.values_list("id", flat=True)
        context['similar_posts'] = similar_posts
        context['comments'] = self.object.comments.filter(active=True)
        return context


