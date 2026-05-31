from django.core.mail import send_mail
from django.db.models import Count
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.contrib.postgres.search import SearchVector,SearchQuery, SearchRank,TrigramSimilarity
from django.views.generic import FormView, ListView, DetailView, View
from taggit.models import Tag
from .models import Post
from .forms import EmailPostForm, CommentForm, Searchforms  # Ensure class name matches your forms.py

class PostSearchView(View):
    def get(self, request):
        form = Searchforms()
        query = None
        results = []
        
        # Pull query from request.GET if it exists
        if 'query' in request.GET:
            form = Searchforms(request.GET)
            if form.is_valid():
                query = form.cleaned_data['query']

                search_vector=SearchVector('title', weight='A') + SearchVector('body', weight='B')
                search_query = SearchQuery(query)
                results = Post.published.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query),
                similarity=TrigramSimilarity("title", query),
                ).filter(
                Q(rank__gte=0.1) |
                Q(similarity__gt=0.1)
                ).order_by("-rank", "-similarity")
        return render(
            request,
            'blog/post/search.html',
            {  # FIX: Wrapped context dictionary variables in curly braces
                'form': form,
                'query': query,
                'results': results
            }
        )


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
            self.template_name,
            {'post': self.post_obj, 'form': form, 'comment': comment}
        )


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 4
    template_name = 'blog/post/list.html'

    def get_queryset(self):
        # FIX: Swapped execution order. Run evaluation logic before fetching super().get_queryset()
        # to ensure self.tag is consistently set before get_context_data() reads it.
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug:
            self.tag = get_object_or_404(Tag, slug=tag_slug)
            return self.queryset.filter(tags__in=[self.tag])
        
        self.tag = None
        return self.queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag

        return context


class PostShareView(FormView):
    form_class = EmailPostForm
    template_name = 'blog/post/share.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(
            Post, id=self.kwargs.get("post_id"), status=Post.Status.PUBLISHED
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.post_obj
        context['sent'] = kwargs.get('sent', False)
        return context

    def form_valid(self, form):
        cd = form.cleaned_data
        post_url = self.request.build_absolute_uri(
            self.post_obj.get_absolute_url()
        ) 
        subject = f"{cd['name']} ({cd['email']}) recommends you read {self.post_obj.title}"
        message = f"Read {self.post_obj.title} at {post_url}\n\n{cd['name']}'s comments: {cd['comments']}"
        send_mail(subject, message, None, [cd['to']])
        return self.render_to_response(self.get_context_data(form=form, sent=True))


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
        context = super().get_context_data(**kwargs)
        
        # Optimization: Fetch tag IDs directly from self.object
        tag_ids = self.object.tags.values_list("id", flat=True)
        
        similar_posts = Post.published.filter(tags__in=tag_ids).exclude(id=self.object.id).distinct()
        similar_posts = similar_posts.annotate(same_tags=Count("tags")).order_by("-same_tags", "-publish")[:4]

        context['form'] = CommentForm()
        context["post_tag_ids"] = tag_ids
        context['similar_posts'] = similar_posts
        context['comments'] = self.object.comments.filter(active=True)
        return context
