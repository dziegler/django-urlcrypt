from django.conf.urls.defaults import *
from django.conf import settings

if settings.RUNNING_TESTS:
    urlpatterns = patterns('urlcrypt.views',
        url(r'^test/view/$', 'test_view', name='urlcrypt_test_view'),  
        url(r'^test/view/(?P<username>.+)/$', 'test_view', name='urlcrypt_test_view_username'),  
    )
else:
    urlpatterns = patterns('')

urlpatterns += patterns('urlcrypt.views',
    url(r'^(?P<token>.+)/$', 'login_redirect', name='urlcrypt_redirect'),  
) 