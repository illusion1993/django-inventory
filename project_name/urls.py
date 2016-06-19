from django.conf.urls.static import static
from django.contrib import admin
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


from project_name.settings import MEDIA_ROOT, MEDIA_URL

admin.autodiscover()

urlpatterns = patterns('',
    # Admin panel and documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(
        r'^admin/',
        include(admin.site.urls)
    ),
    url(
        r'^',
        include('inventory.urls')
    ),
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)