from django.test import TestCase
from django.urls import reverse, resolve
from ..views import BoardListView
from ..models import Board


class HomeTests(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board.')
        url = reverse('home')  # 逆向解析函数
        self.response = self.client.get(url)  # Django在它的TestCase类中已经集成了一个客户端工具，只需调用client属性就可以得到一个客户端

    def test_home_view_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_home_url_resolves_home_view(self):
        view = resolve('/')  # 这里是指网站根路径
        # self.assertEqual(view.func, home)
        self.assertEquals(view.func.view_class, BoardListView)  # 使用CBV类型视图后的断言

    def test_home_view_contains_link_to_topics_page(self):
        board_topics_url = reverse('board_topics', kwargs={'pk': self.board.pk})
        self.assertContains(self.response, 'href="{0}"'.format(board_topics_url))