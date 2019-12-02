from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, ListView

from .forms import NewTopicForm, PostForm
from .models import Board, Topic, Post


# Create your views here

# def home(request):
#     boards = Board.objects.all()
#     # render方法可接收三个参数，一是request参数，二是待渲染的html模板文件，三是保存具体数据的字典参数
#     return render(request, 'home.html', {'boards':boards})

class BoardListView(ListView):  # 使用 GCBV 为模型列表来重写home
    model = Board
    context_object_name = 'boards'
    template_name = 'home.html'

# def board_topics(request, pk):
#     # try:
#     #     board = Board.objects.get(pk=pk)
#     # except Board.DoesNotExist:
#     #     raise Http404
#
#     # Django 有一个快捷方式去得到一个对象，或者返回一个不存在的对象 404。
#     board = get_object_or_404(Board, pk=pk)
#     queryset = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
#     page = request.GET.get('page', 1)
#     paginator = Paginator(queryset, 20)
#
#     try:
#         topics = paginator.page(page)
#     except PageNotAnInteger:
#         # fallback to the first page
#         topics = paginator.page(1)
#     except EmptyPage:
#         # probably the user tried to add a page number
#         # in the url, so we fallback to the last page
#         topics = paginator.page(paginator.num_pages)
#
#     return render(request, 'topics.html', {'board': board, 'topics': topics})

class TopicListView(ListView):  # GCBV 分页
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return queryset


# def new_topic(request, pk):
#     board = get_object_or_404(Board, pk=pk)
#
#     if request.method == 'POST':
#         subject = request.POST['subject']
#         message = request.POST['message']
#
#         user = User.objects.first()   # TODO: 临时使用一个账号作为登录用户
#
#         topic = Topic.objects.create(
#             subject = subject,
#             board = board,
#             starter = user
#         )
#
#         post = Post.objects.create(
#             message = message,
#             topic = topic,
#             created_by = user
#         )
#
#         return redirect('board_topics', pk=board.pk)  # TODO: redirect to the created topic page
#
#     return render(request, 'new_topic.html', {'board':board})

@login_required # Django 有一个内置的 视图装饰器 来避免它被未登录的用户访问
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    user = User.objects.first()  # TODO: get the currently logged in user
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)  # commit=False告诉Django先不提交到数据库.
            topic.board = board              # 添加额外数据
            topic.starter = request.user             # 添加额外数据
            topic.save()                     # 发送到数据库
            post = Post.objects.create(
                message=form.cleaned_data.get('message'),  # cleaned_data 就是读取表单返回的值，返回类型为字典dict型
                topic=topic,
                created_by=request.user
            )
            return redirect('board_topics', pk=board.pk, topic_pk=topic.pk)  # TODO: redirect to the created topic page
    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})  # 传递表单form

# def topic_posts(request, pk, topic_pk):
#     topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
#     topic.views += 1
#     topic.save()
#     return render(request, 'topic_posts.html', {'topic': topic})

class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topic_posts.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):

        session_key = 'viewed_topic_{}'.format(self.topic.pk)  # <--这里
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True           # <--直到这里

        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset


@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_updated = timezone.now()
            topic.save()

            topic_url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
            topic_post_url = '{url}?page={page}#{id}'.format(
                url=topic_url,
                id=post.pk,
                page=topic.get_page_count()
            )

            return redirect(topic_post_url)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})

"""
我们不能用 @login_required 装饰器直接装饰类。我们必须使用一个工具@method_decorator，并传递一个装饰器（或一个装饰器列表）并告诉应该装饰哪个类。
在 CBV 中，装饰调度类是很常见的。它是一个Django内部使用的方法（在View类中定义）。所有的请求都会经过这个类，所以装饰它会相对安全
"""
@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):  # 使用 GCBV 来实现编辑帖子的视图
    model = Post
    fields = ('message', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'   # 标识用于检索 Post 对象的关键字参数的名称
    context_object_name = 'post'  #

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)