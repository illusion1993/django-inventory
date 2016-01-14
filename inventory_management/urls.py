from django.contrib import admin
from django.conf.urls import patterns, include, url

#from manager.views import *
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from manager.newviews import *

# See: https://docs.djangoproject.com/en/dev/ref/contrib/admin/#hooking-adminsite-instances-into-your-urlconf
admin.autodiscover()

def admin_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):

    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and u.is_admin,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def user_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):

    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated(),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

# See: https://docs.djangoproject.com/en/dev/topics/http/urls/
urlpatterns = patterns('',
    # Admin panel and documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^dashboard/$', login_required(DashboardView.as_view(), login_url='login', redirect_field_name=None), name='dashboard'),
    #url(r'^dashboard/$', HttpResponse('Dashboard'), name='dashboard'),
    #url(r'^profile/$', EditProfileView.as_view()),
    #url(r'^itemList/$', ItemListView.as_view()),

    #url(r'^provisionItem/$', ProvisionItemView.as_view(), name='provisionItem'),
    #url(r'^provisionItem/([0-9]+)/$', ProvisionItemView.as_view()),
    #url(r'^addItem/$', AddItemView.as_view()),
    #url(r'^editItem/$', EditItemView.as_view()),
    #url(r'^editItem/([0-9]+)/$', EditItemView.as_view()),
    #url(r'^returnItem/$', ReturnItemView.as_view()),

    #url(r'^requestItem/$', RequestItemView.as_view()),


    url(r'^items/$', login_required(ItemsView.as_view(), login_url='login', redirect_field_name=None), name='items_list'),

    url(r'^items/add/$', admin_required(AddItemView.as_view(), login_url='login', redirect_field_name=None), name='add_items'),
    url(r'^items/(?P<pk>[0-9]+)/$', admin_required(EditItemView.as_view(), login_url='login', redirect_field_name=None), name='edit_items'),

    url(r'^items/request/$', user_required(RequestItemView.as_view(), login_url='login', redirect_field_name=None), name='request_item'),
    url(r'^items/return/$', admin_required(ProvisionListView.as_view(), login_url='login', redirect_field_name=None), name='provision_list'),
    url(r'^items/return/(?P<pk>[0-9]+)/$', admin_required(ReturnItemView.as_view(), login_url='login', redirect_field_name=None), name='return_item'),

    #url(r'^items/request/$', RequestItemView.as_view()),

)
