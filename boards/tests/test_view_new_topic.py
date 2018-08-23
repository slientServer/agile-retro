from django.test import TestCase, Client
from django.urls import reverse, resolve
from ..views import TopicListView
from ..forms import NewTopicForm
from ..models import Board, User, Topic, Post
# Create your tests here.

class NewTopicTests(TestCase):
  """docstring for NewTopicTests"""
  def setUp(self):
    Board.objects.create(name='Djiango', description='Djiango Board.')
    User.objects.create_user(username='john', email='john@doe.com', password='123')
    self.client.login(username='john', password='123')

  def test_new_topic_view_success_status_code(self):
    url=reverse('new_topic', kwargs={'pk': Board.objects.first().id})
    response=self.client.get(url)
    self.assertEquals(response.status_code, 200)

  def test_new_topic_view_not_found_status_code(self):
    url=reverse('new_topic', kwargs={'pk': 99})
    response=self.client.get(url)
    self.assertEquals(response.status_code, 404)

  def test_new_topic_view_contains_link_back_to_board_topics_view(self):
    new_topic_url=reverse('new_topic', kwargs={'pk': Board.objects.first().id})
    board_topics_url=reverse('board_topics', kwargs={'pk': Board.objects.first().id})
    response=self.client.get(new_topic_url)
    self.assertContains(response, 'href="{0}"'.format(board_topics_url))

  def test_csrf(self):
    url=reverse('new_topic', kwargs={'pk': Board.objects.first().id})
    response=self.client.get(url)
    self.assertContains(response, 'csrfmiddlewaretoken')

  def test_new_topic_valid_post_data(self):
    url=reverse('new_topic', kwargs={'pk': Board.objects.first().id})
    data={
      'subject': 'Test title',
      'message': 'Test message hah'
    }
    response=self.client.post(url, data)
    self.assertTrue(Topic.objects.exists())
    self.assertTrue(Post.objects.exists())

  def test_new_topic_invalid_post_data(self):
    '''Invalid post data should not redirect and should show the form again with validataion errors'''
    url=reverse('new_topic', kwargs={'pk': Board.objects.first().id})
    response=self.client.post(url, {})
    self.assertEquals(response.status_code, 200)

  def test_new_topic_invalid_post_data_empty_fields(self):
    url=reverse('new_topic', kwargs={'pk': Board.objects.first().id})
    response=self.client.post(url, {'subject': '', 'message': ''})
    self.assertEquals(response.status_code, 200)
    self.assertFalse(Topic.objects.exists())
    self.assertFalse(Post.objects.exists())

  def test_contains_form(self):
    url=reverse('new_topic', kwargs={'pk': Board.objects.first().id})
    response=self.client.get(url)
    self.assertIsInstance(response.context.get('form'), NewTopicForm)

  def test_new_topic_invalid_post_data(self):  # <- updated this one
    '''
    Invalid post data should not redirect
    The expected behavior is to show the form again with validation errors
    '''
    url = reverse('new_topic', kwargs={'pk': Board.objects.first().id})
    response = self.client.post(url, {})
    form = response.context.get('form')
    self.assertEquals(response.status_code, 200)
    self.assertTrue(form.errors)

class LoginRequiredNewTopicTests(TestCase):
  def setUp(self):
      Board.objects.create(name='Django', description='Django board.')
      self.url = reverse('new_topic', kwargs={'pk': 1})
      self.response = self.client.get(self.url)

  def test_redirection(self):
      login_url = reverse('login')
      self.assertRedirects(self.response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))