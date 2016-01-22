from django.core.urlresolvers import reverse_lazy
from django.test import TestCase
from inventory.models import User


class HomeViewTestCase(TestCase):
    """Test case for home page"""

    def test_home_view_get(self):
        """Testing home page for get request"""
        resp = self.client.get(reverse_lazy('home'))
        self.assertEqual(resp.status_code, 200)

    def test_home_view_post(self):
        """post request not allowed on home page"""
        resp = self.client.post(reverse_lazy('home'))
        self.assertEqual(resp.status_code, 405)


class LoginViewTestCase(TestCase):
    def test_login_view_get(self):
        """Testing login page for get request"""
        resp = self.client.get(reverse_lazy('login'))
        self.assertEqual(resp.status_code, 200)

    def test_login_view_success_post(self):
        """Testing login authentication and message passed"""
        user = User.objects.create_user(
            'test@test.com',
            'test'
        )

        resp = self.client.post(
            reverse_lazy('login'),
            {
                'email': 'test@test.com',
                'password': 'test'
            },
            follow=True
        )

        self.assertEqual(resp.status_code, 200)
        messages = list(resp.context['messages'])
        self.assertEqual(str(messages[0]), 'You have been logged in')

    def test_login_view_failure_post(self):
        """Authentication must fail for wrong credentials"""
        resp = self.client.post(
            reverse_lazy('login'),
            {
                'email': 'test@test.com',
                'password': 'test'
            },
            follow=True
        )

        # Checking status code
        self.assertEqual(resp.status_code, 200)

        # Checking passed message
        messages = list(resp.context['messages'])
        self.assertEqual(str(messages[0]), 'Please check your credentials')


class DashboardViewNoAuthTestCase(TestCase):
    """Testing dashboard view without logging in"""

    def test_dashboard_view_without_login_get(self):
        """Visiting dashboard view without logging in must redirect to login page"""
        resp = self.client.get(reverse_lazy('dashboard'), follow=False)

        # Checking status code
        self.assertEqual(resp.status_code, 302)

        # Now checking by following redirect
        resp = self.client.get(reverse_lazy('dashboard'), follow=True)

        # Checking passed message
        messages = list(resp.context['messages'])
        self.assertEqual(str(messages[0]), 'You need to login First')


class DashboardViewTestCase(TestCase):
    """Testing dashboard view for context and messages"""

    def setUp(self):
        """Setting up authentication for testing dashboard"""
        user = User.objects.create_user(
            'test@test.com',
            'test'
        )

        resp = self.client.post(
            reverse_lazy('login'),
            {
                'email': 'test@test.com',
                'password': 'test'
            },
            follow=True
        )

    def test_dashboard_view_get(self):
        """Testing dashboard on get request after authentication"""
        resp = self.client.get(reverse_lazy('dashboard'), follow=False)

        # Checking status code
        self.assertEqual(resp.status_code, 200)

        # Checking if pending and approved requests are present in context
        self.assertTrue('pending' in resp.context)
        self.assertTrue('approved' in resp.context)