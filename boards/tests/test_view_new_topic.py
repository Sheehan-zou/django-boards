from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse, resolve

from ..forms import NewTopicForm
from ..models import Board, Topic, Post
from ..views import new_topic, PostListView


# class NewTopicTests(TestCase):
#     def setUp(self):
#         Board.objects.create(name='Django', description='Django board.')
#         User.objects.create_user(username='john', email='john@doe.com', password='123')
#
#     def test_new_topic_view_success_status_code(self):
#         url = reverse('new_topic', kwargs={'pk':1})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#
#     def test_new_topic_view_not_found_status_code(self):
#         url = reverse('new_topic', kwargs={'pk': 99})
#         response = self.client.get(url)
#         self.assertEquals(response.status_code, 404)
#
#     def test_new_topic_url_resolves_new_topic_view(self):
#         view = resolve('/boards/1/new/')
#         self.assertEquals(view.func, new_topic)
#
#     def test_new_topic_view_contains_link_back_to_board_topics_view(self):
#         new_topic_url = reverse('new_topic', kwargs={'pk': 1})
#         board_topics_url = reverse('board_topics', kwargs={'pk': 1})
#         response = self.client.get(new_topic_url)
#         self.assertContains(response, 'href="{0}"'.format(board_topics_url))
#
#     def test_csrf(self):
#         url = reverse('new_topic', kwargs={'pk': 1})
#         response = self.client.get(url)
#         self.assertContains(response, 'csrfmiddlewaretoken')
#
#     def test_new_topic_valid_post_data(self):
#         url = reverse('new_topic', kwargs={'pk': 1})
#         data = {
#             'subject': 'Test title',
#             'message': 'Lorem ipsum dolor sit amet'
#         }
#         response = self.client.post(url, data)
#         self.assertTrue(Topic.objects.exists())
#         self.assertTrue(Post.objects.exists())
#
#     def test_new_topic_invalid_post_data(self):
#         '''
#         Invalid post data should not redirect
#         The expected behavior is to show the form again with validation errors
#         '''
#         url = reverse('new_topic', kwargs={'pk': 1})
#         response = self.client.post(url, {})
#         form = response.context.get('form')
#         self.assertEquals(response.status_code, 200)
#         self.assertTrue(form.errors)
#
#     def test_new_topic_invalid_post_data_empty_fields(self):
#         '''
#         Invalid post data should not redirect
#         The expected behavior is to show the form again with validation errors
#         '''
#         url = reverse('new_topic', kwargs={'pk': 1})
#         data = {
#             'subject': '',
#             'message': ''
#         }
#         response = self.client.post(url, data)
#         self.assertEquals(response.status_code, 200)
#         self.assertFalse(Topic.objects.exists())
#         self.assertFalse(Post.objects.exists())
#
#     def test_contains_form(self):
#         url = reverse('new_topic', kwargs={'pk':1})
#         response = self.client.get(url)  # 返回Response对象，拥有context属性
#         # context：用来渲染模板的context实例。如果页面使用了多个模板,那context就会是Context Object列表.它们的排序方式就是它们被渲染的顺序。
#         form = response.context.get('form')
#         self.assertIsInstance(form, NewTopicForm)


class LoginRequiredNewTopicTests(TestCase):
   def setUp(self):
       Board.objects.create(name='Django', description='Django board.')
       self.url = reverse('new_topic', kwargs={'pk': 1})
       self.response = self.client.get(self.url)

   def test_redirection(self):
       login_url = reverse('login')
       self.assertRedirects(self.response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

class TopicPostsTests(TestCase):
    def setUp(self):
        board = Board.objects.create(name='Django', description='Django board.')
        user = User.objects.create_user(username='john', email='john@doe.com', password='123')
        topic = Topic.objects.create(subject='Hello, world', board=board, starter=user)
        Post.objects.create(message='Lorem ipsum dolor sit amet', topic=topic, created_by=user)
        url = reverse('topic_posts', kwargs={'pk': board.pk, 'topic_pk': topic.pk})
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/boards/1/topics/1/')
        # self.assertEquals(view.func, topic_posts)
        self.assertEquals(view.func.view_class, PostListView)