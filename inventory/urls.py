"""Inventory App URLs"""
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from inventory.views import (
    DashboardView,
    LogoutView,
    ProfileView,
    EditProfileView,
    ItemsListView,
    AddItemView,
    EditItemView,
    RequestItemView,
    ProvisionListView,
    ReturnItemView,
    ProvisionItemView,
    ProvisionByRequestView,
    EditItemListView,
    LoadMoreView, ImageUploadView, UserAutocompleteView,
    ItemAutocompleteView, ReportView, ReportAjaxView, LoginFormView)
from inventory.decorators import (
    admin_required,
    anonymous_required
)


urlpatterns = patterns(
    '',

    # urls available to both users and admins
    url(
        r'^$',
        TemplateView.as_view(template_name='home.html'),
        name="home"
    ),
    url(
        r'^login/$',
        anonymous_required(
            LoginFormView.as_view(),
            redirect_to='dashboard'
        ),
        name="login"
    ),
    url(
        r'^logout/$',
        LogoutView.as_view(),
        name="logout"
    ),
    url(
        r'^dashboard/$',
        login_required(
            DashboardView.as_view()
        ),
        name="dashboard"
    ),
    url(
        r'^profile/$',
        login_required(
            ProfileView.as_view()
        ),
        name="profile"
    ),
    url(
        r'^profile/edit/$',
        login_required(
            EditProfileView.as_view()
        ),
        name="edit_profile"
    ),
    url(
        r'^items/$',
        login_required(
            ItemsListView.as_view()
        ),
        name="items_list"
    ),

    # urls for admin only
    url(
        r'^items/add/$',
        admin_required(
            AddItemView.as_view()
        ),
        name="add_item"
    ),
    url(
        r'^items/edit/$',
        admin_required(
            EditItemListView.as_view()
        ),
        name='edit_item_list'
    ),
    url(
        r'^items/edit/(?P<pk>[\d]+)/$',
        admin_required(
            EditItemView.as_view()
        ),
        name='edit_item'
    ),
    url(
        r'^items/return/$',
        admin_required(
            ProvisionListView.as_view()
        ),
        name='provision_list'
    ),
    url(
        r'^items/return/(?P<pk>[\d]+)/$',
        admin_required(
            ReturnItemView.as_view()
        ),
        name='return_item'
    ),
    url(
        r'^items/provision/$',
        admin_required(
            ProvisionItemView.as_view()
        ),
        name='provision_item'
    ),
    url(
        r'^items/provision/(?P<pk>[\d]+)/$',
        admin_required(
            ProvisionByRequestView.as_view()
        ),
        name='provision_by_request'
    ),
    url(
        r'^report/$',
        admin_required(
            ReportView.as_view()
        ),
        name='report'
    ),
    url(
        r'^report/ajax/$',
        admin_required(
            ReportAjaxView.as_view()
        ),
        name='report_ajax'
    ),

    # urls for user role (but admin can also access)
    url(
        r'^request/$',
        login_required(
            RequestItemView.as_view()
        ),
        name='request_item'
    ),

    # urls to handle AJAX requests
    url(
        r'^ajax/load_more/$',
        login_required(
            LoadMoreView.as_view()
        ),
        name="load_more_ajax"
    ),
    url(
        r'^ajax/upload_image/$',
        login_required(
            ImageUploadView.as_view()
        ),
        name="image_upload_ajax"
    ),
    url(
        r'^ajax/user_autocomplete/$',
        admin_required(
            UserAutocompleteView.as_view(),
        ),
        name="user_autocomplete_ajax"
    ),
    url(
        r'^ajax/item_autocomplete/$',
        admin_required(
            ItemAutocompleteView.as_view(),
        ),
        name="item_autocomplete_ajax"
    ),
)
