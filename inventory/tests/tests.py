from django.core.urlresolvers import reverse_lazy
from django.test import TestCase
from inventory.models import User, Item
from inventory.message_constants import *


class AnonymousTestCase(TestCase):
    """
    Test cases for an anonymous user
    """

    # Adding fixture for initial data
    fixtures = ['data.json']

    def test_home_view_get(self):
        """
        Testing home page for get request
        """
        resp = self.client.get(reverse_lazy('home'))
        self.assertEqual(resp.status_code, 200)

    def test_home_view_post(self):
        """
        Post request not allowed on home page
        """
        resp = self.client.post(reverse_lazy('home'))
        self.assertEqual(resp.status_code, 405)

    def test_login_view_get(self):
        """
        Anonymous user visits the login page
        """
        resp = self.client.get(reverse_lazy('login'))

        # Checking status code
        self.assertEqual(resp.status_code, 200)

    def test_login_view_success_post(self):
        """
        Testing successful login authentication and message passed
        """
        resp = self.client.post(
            reverse_lazy('login'),
            {
                'email': 'user@user.com',
                'password': 'user'
            },
            follow=True
        )

        self.assertEqual(resp.status_code, 200)
        messages = list(resp.context['messages'])
        self.assertEqual(str(messages[0]), LOGIN_SUCCESS_MESSAGE)

    def test_login_view_failure_post(self):
        """
        Authentication must fail for wrong credentials
        """
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
        self.assertEqual(str(messages[0]), LOGIN_INVALID_MESSAGE)

    def test_logout_view_get(self):
        """
        Anonymous user must see 404 on logout page
        """
        resp = self.client.get(reverse_lazy('logout'))

        # Checking status code
        self.assertEqual(resp.status_code, 404)

    def test_dashboard_view_get(self):
        """
        Anonymous user must be redirected to login page from dashboard
        """
        resp = self.client.get(reverse_lazy('dashboard'), follow=False)

        # Checking status code
        self.assertEqual(resp.status_code, 302)

        # Now checking by following redirect
        resp = self.client.get(reverse_lazy('dashboard'), follow=True)

        # Checking passed message
        messages = list(resp.context['messages'])
        self.assertEqual(str(messages[0]), LOGIN_REQUIRED_MESSAGE)

    def test_dashboard_view__post(self):
        """
        Post request on dashboard view without logging in
        """
        resp = self.client.post(reverse_lazy('dashboard'))

        # Checking status code
        self.assertEqual(resp.status_code, 302)

    def test_profile_view_get(self):
        """
        Anonymous user must be redirected to login page from profile view
        """
        resp = self.client.get(reverse_lazy('profile'), follow=False)

        # Checking status code
        self.assertEqual(resp.status_code, 302)

        # Now checking by following redirect
        resp = self.client.get(reverse_lazy('profile'), follow=True)

        # Checking passed message
        messages = list(resp.context['messages'])
        self.assertEqual(str(messages[0]), LOGIN_REQUIRED_MESSAGE)

    def test_profile_view__post(self):
        """
        Anonymous user must be redirected to login page from profile view
        """
        resp = self.client.post(reverse_lazy('profile'))

        # Checking status code
        self.assertEqual(resp.status_code, 302)

        # Now checking by following redirect
        resp = self.client.get(reverse_lazy('profile'), follow=True)

        # Checking passed message
        messages = list(resp.context['messages'])
        self.assertEqual(str(messages[0]), LOGIN_REQUIRED_MESSAGE)

    def test_edit_profile_view_get(self):
        """
        Anonymous user must be redirected to login page from edit profile view
        """
        resp = self.client.get(reverse_lazy('edit_profile'), follow=False)

        # Checking status code
        self.assertEqual(resp.status_code, 302)

        # Now checking by following redirect
        resp = self.client.get(reverse_lazy('edit_profile'), follow=True)

        # Checking passed message
        messages = list(resp.context['messages'])
        self.assertEqual(str(messages[0]), LOGIN_REQUIRED_MESSAGE)

    def test_edit_profile_view_post(self):
        """
        Anonymous user must be redirected to login page from edit profile view
        """
        resp = self.client.post(reverse_lazy('edit_profile'))

        # Checking status code
        self.assertEqual(resp.status_code, 302)

        # Now checking by following redirect
        resp = self.client.get(reverse_lazy('edit_profile'), follow=True)

        # Checking passed message
        messages = list(resp.context['messages'])
        self.assertEqual(str(messages[0]), LOGIN_REQUIRED_MESSAGE)

    def test_add_item_view_get(self):
        """
        Anonymous user must be redirected to login page from add item view
        """
        resp = self.client.get(reverse_lazy('add_item'), follow=False)

        # Checking status code
        self.assertEqual(resp.status_code, 302)

        # Now checking by following redirect
        resp = self.client.get(reverse_lazy('add_item'), follow=True)

        # Checking passed message
        messages = list(resp.context['messages'])
        self.assertEqual(str(messages[0]), LOGIN_REQUIRED_MESSAGE)

    def test_add_item_view_post(self):
        """
        Anonymous user must be redirected to login page from add item view
        """
        resp = self.client.post(reverse_lazy('add_item'))

        # Checking status code
        self.assertEqual(resp.status_code, 302)

        # Now checking by following redirect
        resp = self.client.get(reverse_lazy('add_item'), follow=True)

        # Checking passed message
        messages = list(resp.context['messages'])
        self.assertEqual(str(messages[0]), LOGIN_REQUIRED_MESSAGE)

    def test_edit_item_list_view_get(self):
        """
        Anonymous user must be redirected to login page from edit item list view
        """
        resp = self.client.get(reverse_lazy('edit_item_list'), follow=False)

        # Checking status code
        self.assertEqual(resp.status_code, 302)

        # Now checking by following redirect
        resp = self.client.get(reverse_lazy('edit_item_list'), follow=True)

        # Checking passed message
        messages = list(resp.context['messages'])
        self.assertEqual(str(messages[0]), LOGIN_REQUIRED_MESSAGE)

    def test_edit_item_list_view_post(self):
        """
        Anonymous user must be redirected to login page from add item view
        """
        resp = self.client.post(reverse_lazy('edit_item_list'))

        # Checking status code
        self.assertEqual(resp.status_code, 302)

        # Now checking by following redirect
        resp = self.client.get(reverse_lazy('edit_item_list'), follow=True)

        # Checking passed message
        messages = list(resp.context['messages'])
        self.assertEqual(str(messages[0]), LOGIN_REQUIRED_MESSAGE)




class UserTestCase(TestCase):
    """
    Test cases for a logged in inventory user
    """

    # Adding fixture for initial data
    fixtures = ['data.json']

    def setUp(self):
        """
        Logging in the user
        """
        self.user = User.objects.create_user(
            email='test@test.com',
            password='test',
            first_name='Test',
            last_name='User',
            phone='9997609994',
            address='Gurgaon',
            id_number='PBX024',
            is_admin=False,
        )

        resp = self.client.post(
            reverse_lazy('login'),
            {
                'email': 'test@test.com',
                'password': 'test'
            },
            follow=True
        )

    def test_home_view_get(self):
        """
        Testing home page for get request
        """
        resp = self.client.get(reverse_lazy('home'))
        self.assertEqual(resp.status_code, 200)

    def test_home_view_post(self):
        """
        Post request not allowed on home page
        """
        resp = self.client.post(reverse_lazy('home'))
        self.assertEqual(resp.status_code, 405)

    def test_login_view_get(self):
        """
        Login View must redirect the user to dashboard
        """
        # Visiting login view after logging in must redirect to dashboard page
        resp = self.client.get(reverse_lazy('login'), follow=False)

        # Checking status code
        self.assertEqual(resp.status_code, 302)

        # Now checking by following redirect
        resp = self.client.get(reverse_lazy('login'), follow=True)

        # Checking passed message
        messages = list(resp.context['messages'])
        self.assertEqual(str(messages[0]), ALREADY_LOGGED_MESSAGE)

    def test_login_view_post(self):
        """
        Login View must redirect the user to dashboard
        """
        # Visiting login view after logging in must redirect to dashboard page
        resp = self.client.post(reverse_lazy('login'), follow=False)

        # Checking status code
        self.assertEqual(resp.status_code, 302)

        # Now checking by following redirect
        resp = self.client.post(reverse_lazy('login'), follow=True)

        # Checking passed message
        messages = list(resp.context['messages'])
        self.assertEqual(str(messages[0]), ALREADY_LOGGED_MESSAGE)

    def test_logout_view_no_follow_get(self):
        """
        Inventory user logs out using LogoutView
        """
        # User Visiting logout page, not following the redirect
        resp = self.client.get(reverse_lazy('logout'), follow=False)

        # Logout View must return a HttpResponseRedirect
        self.assertEqual(resp.status_code, 302)

    def test_logout_view_follow_get(self):
        """
        Inventory user logs out using LogoutView
        """
        # User Visiting logout page, following the redirect
        resp = self.client.get(reverse_lazy('logout'), follow=True)

        # Logout View must redirect the user to login page
        self.assertEqual(resp.status_code, 200)

        # Message for successful logout must be passed
        messages = list(resp.context['messages'])
        self.assertEqual(str(messages[0]), LOGOUT_SUCCESS_MESSAGE)

    def test_logout_view_post(self):
        """
        POST request sent on logout view by inventory user
        """
        resp = self.client.post(reverse_lazy('logout'))

        # Checking status code, should be 405 method not allowed
        self.assertEqual(resp.status_code, 405)

    def test_dashboard_view_get(self):
        """
        Inventory user visits the dashboard page
        """
        resp = self.client.get(reverse_lazy('dashboard'))

        # Checking status code
        self.assertEqual(resp.status_code, 200)

        # Checking if pending and approved requests are present in context
        self.assertTrue('pending' in resp.context)
        self.assertTrue('approved' in resp.context)

        # Checking user type constants in context
        self.assertTrue('is_admin' in resp.context)
        self.assertTrue('is_user' in resp.context)

        # is_admin must be false in context and is_user must be true
        self.assertEqual(resp.context['is_admin'], False)
        self.assertEqual(resp.context['is_user'], True)

    def test_dashboard_view_post(self):
        """
        Inventory user sends a POST request on dashboard
        """
        resp = self.client.post(reverse_lazy('dashboard'))

        # Status code must be 405, due to post method not allowed
        self.assertEqual(resp.status_code, 405)

    def test_profile_view_get(self):
        """
        Test for inventory user visiting profile view
        """
        resp = self.client.get(reverse_lazy('profile'))

        # Checking status code, must be 200
        self.assertEqual(resp.status_code, 200)

        # Checking if user object is present in context
        self.assertTrue('user' in resp.context)

    def test_profile_view_post(self):
        """
        Inventory user sending a POST request on profile view
        """
        resp = self.client.post(reverse_lazy('profile'))

        # Checking status code, must be 405 method not allowed
        self.assertEqual(resp.status_code, 405)

    def test_edit_profile_view_get(self):
        """
        Test for inventory user edit profile view
        """
        resp = self.client.get(reverse_lazy('edit_profile'))

        # Checking status code, must be 200
        self.assertEqual(resp.status_code, 200)

        # Checking if user object is present in context
        self.assertTrue('user' in resp.context)

    def test_edit_profile_view_post(self):
        """
        Test edit profile view when inventory user submits changes
        """

        # Check all form errors when all form fields empty
        resp = self.client.post(reverse_lazy('edit_profile'), {})
        self.assertFormError(
            resp,
            'form',
            'first_name',
            u'This field is required.'
        )
        self.assertFormError(
            resp,
            'form',
            'last_name',
            u'This field is required.'
        )
        self.assertFormError(
            resp,
            'form',
            'phone',
            u'This field is required.'
        )
        self.assertFormError(
            resp,
            'form',
            'address',
            u'This field is required.'
        )
        self.assertFormError(
            resp,
            'form',
            'id_number',
            u'This field is required.'
        )

        # Form error when invalid first name entered
        resp = self.client.post(reverse_lazy('edit_profile'), {
            'first_name': '123ABC'
        })
        self.assertFormError(
            resp,
            'form',
            'first_name',
            u'Please enter a valid name'
        )

        # Form error when invalid last name entered
        resp = self.client.post(reverse_lazy('edit_profile'), {
            'last_name': '123ABC'
        })
        self.assertFormError(
            resp,
            'form',
            'last_name',
            u'Please enter a valid name'
        )

        # Form error when invalid phone number entered
        resp = self.client.post(reverse_lazy('edit_profile'), {
            'phone': '123'
        })
        self.assertFormError(
            resp,
            'form',
            'phone',
            u'Please enter a valid phone number. Only 10 digits allowed.'
        )

        # Form error when empty image is submitted
        f = open('inventory/tests/bad_image.jpg')

        resp = self.client.post(reverse_lazy('edit_profile'), {
            'image': f
        })

        f.close()

        self.assertFormError(
            resp,
            'form',
            'image',
            u'The submitted file is empty.'
        )

        # Form error when an invalid image is submitted
        f = open('inventory/tests/bad_image_1.jpg')

        resp = self.client.post(reverse_lazy('edit_profile'), {
            'image': f
        })

        f.close()

        self.assertFormError(
            resp,
            'form',
            'image',
            u'Upload a valid image. The file you uploaded was either not an image or a corrupted image.'
        )

        # Test successful profile update after valid data is submitted
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '9997809995',
            'address': 'New York',
            'id_number': 'PXZ024',
        }

        resp = self.client.post(reverse_lazy('edit_profile'), data)

        # Form must redirect to profile page, 302 status code
        self.assertEqual(resp.status_code, 302)

        # Checking if the profile is updated with new data
        resp = self.client.get(reverse_lazy('edit_profile'))

        form = resp.context['form']
        form_data = form.initial

        for key in data:
            self.assertEqual(form_data[key], data[key])

    def test_request_item_view_get(self):
        """
        Testing the request item view for inventory user
        """
        resp = self.client.get(reverse_lazy('request_item'))
        self.assertEqual(resp.status_code, 200)

        # Test if the form is in the context
        self.assertTrue('form' in resp.context)

        # Test if all the items have quantity greater than 0
        items = resp.context['form']['item'].field.queryset

        for item in items:
            self.assertGreater(item.quantity, 0)

    def test_request_item_view_post(self):
        """
        Testing the request item view when an item is requested
        """

        # Successfully requesting for an item
        resp = self.client.post(reverse_lazy('request_item'), {
            'item': '1'
        }, follow=True)

        # User must be redirected to dashboard with request added
        self.assertEqual(resp.status_code, 200)

        # Checking if the request is added in pending requests
        pending = resp.context['pending']
        self.assertEqual(1, pending[0].item.id)

        # Check form error if invalid item is requested by user
        resp = self.client.post(reverse_lazy('request_item'), {
            'item': '1000'
        }, follow=True)

        self.assertFormError(
            resp,
            'form',
            'item',
            u'Select a valid choice. That choice is not one of the available choices.'
        )


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


class LoginViewNoAuthTestCase(TestCase):
    """Testing login view without being logged in already"""

    def test_login_view_get(self):
        """Testing login page for get request"""
        resp = self.client.get(reverse_lazy('login'))
        self.assertEqual(resp.status_code, 200)

    def test_login_view_success_post(self):
        """Testing successful login authentication and message passed"""
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
        self.assertEqual(str(messages[0]), LOGIN_SUCCESS_MESSAGE)

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
        self.assertEqual(str(messages[0]), LOGIN_INVALID_MESSAGE)


class LoginViewAuthTestCase(TestCase):
    """Testing login view after being logged in already"""

    def setUp(self):
        """Setting up authentication before testing"""
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

    def test_login_view_get(self):
        """This must redirect user to dashboard page"""

        # Visiting login view after logging in must redirect to dashboard page
        resp = self.client.get(reverse_lazy('login'), follow=False)

        # Checking status code
        self.assertEqual(resp.status_code, 302)

        # Now checking by following redirect
        resp = self.client.get(reverse_lazy('login'), follow=True)

        # Checking passed message
        messages = list(resp.context['messages'])
        self.assertEqual(str(messages[0]), ALREADY_LOGGED_MESSAGE)


class LogoutViewNoAuthTestCase(TestCase):
    """Testing logout view when not authenticated"""

    def test_logout_view_without_login_get(self):
        """GET request on logout view by anonymous user"""
        resp = self.client.get(reverse_lazy('logout'))

        # Checking status code, should be 404 for anonymous user
        self.assertEqual(resp.status_code, 404)

    def test_logout_view_without_login_post(self):
        """POST request on logout view by anonymous user"""
        resp = self.client.post(reverse_lazy('logout'))

        # Checking status code, should be 404 for anonymous user
        self.assertEqual(resp.status_code, 405)


class LogoutViewAuthTestCase(TestCase):
    """Testing logout view when user authenticated"""

    def setUp(self):
        """Setting up authentication before testing"""
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

    def test_logout_view_with_login_get(self):
        """GET request on logout view by authenticated user"""
        resp = self.client.get(reverse_lazy('logout'))

        # Checking status code, should be 302 for authenticated user
        self.assertEqual(resp.status_code, 302)

    def test_logout_view_with_login_post(self):
        """POST request on logout view by authenticated user"""
        resp = self.client.post(reverse_lazy('logout'))

        # Checking status code, should be 405 method not allowed
        self.assertEqual(resp.status_code, 405)


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
        self.assertEqual(str(messages[0]), LOGIN_REQUIRED_MESSAGE)

    def test_dashboard_view_without_login_post(self):
        """Post request on dashboard view without logging in"""
        resp = self.client.post(reverse_lazy('dashboard'))

        # Checking status code
        self.assertEqual(resp.status_code, 302)


class DashboardViewAuthTestCase(TestCase):
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

        # Checking user type in context
        self.assertTrue('is_admin' in resp.context)
        self.assertTrue('is_user' in resp.context)

    def test_dashboard_view_post(self):
        """Testing dashboard for post request"""
        resp = self.client.post(reverse_lazy('dashboard'))

        # Status code must be 405, due to post method not allowed
        self.assertEqual(resp.status_code, 405)


class ProfileViewNoAuthTestCase(TestCase):
    """Testing profile view without authenticating"""

    def test_profile_view_without_login_get(self):
        """GET request on profile view without authentication"""
        resp = self.client.get(reverse_lazy('profile'), follow=False)

        # Checking status code
        self.assertEqual(resp.status_code, 302)

        # Now checking by following redirect
        resp = self.client.get(reverse_lazy('dashboard'), follow=True)

        # Checking passed message
        messages = list(resp.context['messages'])
        self.assertEqual(str(messages[0]), LOGIN_REQUIRED_MESSAGE)

    def test_profile_view_without_login_post(self):
        """Post request on profile view without logging in"""
        resp = self.client.post(reverse_lazy('profile'))

        # Checking status code
        self.assertEqual(resp.status_code, 302)


class ProfileViewAuthTestCase(TestCase):
    """Testing profile view for authenticated user"""

    def setUp(self):
        """Setting up authentication for testing profile"""
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

    def test_profile_view_with_login_get(self):
        """Testing profile view on get request after authentication"""
        resp = self.client.get(reverse_lazy('profile'), follow=False)

        # Checking status code
        self.assertEqual(resp.status_code, 200)

        # Checking if user object is present in context
        self.assertTrue('user' in resp.context)

    def test_profile_view_with_login_post(self):
        """Testing profile_view for post request"""
        resp = self.client.post(reverse_lazy('profile'))

        # Status code must be 405, due to post method not allowed
        self.assertEqual(resp.status_code, 405)