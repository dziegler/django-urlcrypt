from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse

from urlcrypt import lib as urlcrypt
from urlcrypt.conf import URLCRYPT_LOGIN_URL

#@rate_limit(num=30)
def login_redirect(request, token):
    try:
        decoded_data = urlcrypt.decode_login_token(token)
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