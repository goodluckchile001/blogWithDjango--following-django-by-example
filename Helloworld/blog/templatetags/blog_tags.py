from django import template
from ..models import Post
from django.db.models import Count
import markdown
from django.utils.safestring import mark_safe


register = template.Library()

@register.simple_tag
def total_post():
    return Post.published.count()

@register.inclusion_tag("blog/post/latest_posts.html")
def show_latest_posts(count=5):
    latest_post = Post.published.order_by('-publish')[:count]
    return {'latest_post':latest_post}
@register.simple_tag
def most_commented_posts(count=5):
    most_commented = Post.published.annotate(total_comments= Count('comments')).order_by('-total_comments')[:count]

    return most_commented

@register.filter(name="markdown")
def markdown_format(text):
    return mark_safe(markdown.markdown(text))
