from django.conf.urls import patterns, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from inventory.views import (
    LoginView,
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
    EditItemListView
)
from inventory.decorators import (
    admin_required,
    user_required,
)

admin.autodiscover()

inventory_urlpatterns = patterns('',
    # urls available to both users and admins
    url(r'^$', TemplateView.as_view(template_name='home.html'), name="home"),
    url(r'^login/$', LoginView.as_view(), name="login"),
    url(r'^logout/$', LogoutView.as_view(), name="logout"),
    url(r'^dashboard/$', login_required(DashboardView.as_view(), login_url='login'), name="dashboard"),
    url(r'^profile/$', login_required(ProfileView.as_view(), login_url='login'), name="profile"),
    url(r'^profile/edit/$', login_required(EditProfileView.as_view(), login_url='login'), name="edit_profile"),
    url(r'^items/$', login_required(ItemsListView.as_view(), login_url='login'), name="items_list"),

    # urls for admin only
    url(r'^items/add/$', admin_required(AddItemView.as_view()), name="add_item"),
    url(r'^items/edit/$', admin_required(EditItemListView.as_view()), name='edit_item_list'),
    url(r'^items/edit/(?P<pk>[0-9]+)/$', admin_required(EditItemView.as_view()), name='edit_item'),
    url(r'^items/return/$', admin_required(ProvisionListView.as_view()), name='provision_list'),
    url(r'^items/return/(?P<pk>[0-9]+)/$', admin_required(ReturnItemView.as_view()), name='return_item'),
    url(r'^items/provision/$', admin_required(ProvisionItemView.as_view()), name='provision_item'),
    url(r'^items/provision/(?P<pk>[0-9]+)/$', admin_required(ProvisionByRequestView.as_view()), name='provision_by_request'),

    # urls for user only
    url(r'^request/$', user_required(RequestItemView.as_view()), name='request_item'),
)