from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden

from urlcrypt.conf import URLCRYPT_LOGIN_URL, URLCRYPT_RATE_LIMIT
from urlcrypt.lib import decode_login_token

# import encode_token and decode_token from correct backend

def rate_limit(num=60):
    """
    Limits the number of requests made by a unique visitor to this view to num per minute.
    """
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            cache_key = 'rate_limit.%s' % request.session._session_key
            added = cache.add(cache_key, 1, timeout=60)
            if added:
                num_tries = 1
            else:
                num_tries = cache.incr(cache_key, delta=1)
            if num_tries > num:
                raise HttpResponseForbidden("Rate Limit Exceeded")
            return func(request, *args, **kwargs)
        return wrapper
    return decorator
    
@rate_limit(num=URLCRYPT_RATE_LIMIT)
def login_redirect(request, token):
    try:
        decoded_data = decode_login_token(token)
    except Exception, ex:
        return HttpResponseRedirect(URLCRYPT_LOGIN_URL)

    if request.user.is_authenticated() and request.user.id == decoded_data['user_id']:
        return HttpResponseRedirect(decoded_data['url'])
    
    user = authenticate(decoded_data=decoded_data)
    if user:
        auth_login(request, user)
        return HttpResponseRedirect(decoded_data['url'])
    else:
        return HttpResponseRedirect(URLCRYPT_LOGIN_URL)
    
@login_required
def test_view(request, username=None):
    return HttpResponse("ok")