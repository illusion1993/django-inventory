from django.conf.urls.static import static
from django.contrib import admin
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
from inventory.views import LoginView, DashboardView, LogoutView, ProfileView, ProfileUpdateView, ItemsView, AddItemView, \
    EditItemView, RequestItemView, ProvisionListView, ReturnItemView, ProvisionItemView, ProvisionItemByRequestView, \
    EditItemsListView
from project_name.settings import MEDIA_ROOT, MEDIA_URL

admin.autodiscover()

def group_required(*group_name):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated():
            if (group_name == "user" and not u.is_admin) | (group_name == "admin" and u.is_admin):
                print "Passed in groups"
                return True
        print "Failed in groups"
        return False

    return user_passes_test(in_groups)


# See: https://docs.djangoproject.com/en/dev/topics/http/urls/
urlpatterns = patterns('',
    # Admin panel and documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', TemplateView.as_view(template_name='home.html')),
    url(r'^login/$', LoginView.as_view(), name="login"),
    url(r'^logout/$', LogoutView.as_view(), name="logout"),
    url(r'^dashboard/$', login_required(DashboardView.as_view(), login_url='login'), name="dashboard"),
    url(r'^profile/$', login_required(ProfileView.as_view(), login_url='login'), name="profile"),
    url(r'^profile/edit/$', login_required(ProfileUpdateView.as_view(), login_url='login'), name="edit_profile"),
    url(r'^items/$', login_required(ItemsView.as_view(), login_url='login'), name="items_list"),

    # urls for admin only
    url(r'^items/add/$', login_required(AddItemView.as_view(), login_url='login'), name="add_item"),
    url(r'^items/edit/$', login_required(EditItemsListView.as_view(), login_url='login'), name='edit_item_list'),
    url(r'^items/edit/(?P<pk>[0-9]+)/$', login_required(EditItemView.as_view(), login_url='login'), name='edit_item'),
    url(r'^items/return/$', login_required(ProvisionListView.as_view(), login_url='login', redirect_field_name=None), name='provision_list'),
    url(r'^items/return/(?P<pk>[0-9]+)/$', login_required(ReturnItemView.as_view(), login_url='login', redirect_field_name=None), name='return_item'),
    url(r'^items/provision/$', login_required(ProvisionItemView.as_view(), login_url='login'), name='provision_form'),
    url(r'^items/provision/(?P<pk>[0-9]+)/$', login_required(ProvisionItemByRequestView.as_view(), login_url='login'), name='provision_by_request'),

    # urls for user only
    url(r'^request/$', login_required(RequestItemView.as_view(), login_url='login'), name='request_item'),
)
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)