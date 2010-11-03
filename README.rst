django-urlcrypt
=================

django-urlcrypt encrypts information in urls, such as login credentials. 

For example, assume I have url patterns that looks like this::

    urlpatterns = patterns('',
        url(r'^inbox/$', 'message_inbox', name='message_inbox'), 
        (r'^r/', include('urlcrypt.urls')),
    )

I can use django-urlcrypt to generate a url for a user that looks like::

    http://www.mydomain.com/r/TkNJBkNFAghDWkdFGPUAQEfcDUJfEBIREgEUFl1BQ18IQkdDUUcPSh4ADAYAWhYKHh8KHBsHEw

and will automatically log that person in and redirects them to ``/inbox/``.

Installation
************

1. ``easy_install django-urlcrypt`` or ``pip install django-urlcrypt``
    
2. Add ``urlcrypt`` to your ``INSTALLED_APPS``

3. In settings.py add ``'urlcrypt.auth_backends.UrlCryptBackend'`` to ``AUTHENTICATION_BACKENDS``

4. In urls.py add::

    (r'^r/', include('urlcrypt.urls')),
    
5. If you wish to use RSA encryption on your tokens, set ``URLCRYPT_USE_RSA_ENCRYPTION = True`` in your settings, generate a private key with ``ssh-keygen -t rsa -f <path to private key>`` and then set the path to the private key as URLCRYPT_PRIVATE_KEY_PATH.  RSA encryption makes the token much longer but is more secure.  The ``pycrypto`` library is required.

Usage
******
In a view::

    from django.core.urlresolvers import reverse
    from urlcrypt import lib as urlcrypt
    
    token = urlcrypt.generate_login_token(user, reverse('message_inbox'))
    encoded_url = reverse('urlcrypt_redirect', args=(token,))
    # yours will look slightly different because you have a different SECRET_KEY, but approximately 
    # encoded_url == /r/TkNJBkNFAghDWkdFGPUAQEfcDUJfEBIREgEUFl1BQ18IQkdDUUcPSh4ADAYAWhYKHh8KHBsHEw
    
In a template::

    {% load urlcrypt_tags %}
    <a href="{% encoded_url user message_inbox %}">click me to log in as {{user.username}} and go to {% url message_inbox %}</a>

Advanced lib usage::

    from urlcrypt import lib as urlcrypt
    
    message = {
        'url': u'/users/following/', 
        'user_id': '12345'
    }
    
    token = urlcrypt.encode_token(message['user_id'], message['url'])
    decoded_message = urlcrypt.decode_token(token, ('user_id', 'url', 'timestamp'))
    
    >>> print token
    TkNJBkNFAghDWkdFGPUAQEfcDUJfEBIREgEUFl1BQ18IQkdDUUcPSh4ADAYAWhYKHh8KHBsHEw
    
    >>> print decoded_message
    {'url': '/users/following/', 'user_id': '12345'}
    
Settings
********

 - ``URLCRYPT_LOGIN_URL``
 
   - default: ``LOGIN_URL``
   - If urlcrypt authentication fails, redirects to ``URLCRYPT_LOGIN_URL``.

 - ``URLCRYPT_RATE_LIMIT``
  
   - default: ``60``
   - The number of urlcrypt requests a unique visitor is allowed to make per minute.

 - ``URLCRYPT_USE_RSA_ENCRYPTION``
 
   - default: ``False``
   - Set ``URLCRYPT_USE_RSA_ENCRYPTION`` to True to enable RSA encryption of tokens.

 - ``URLCRYPT_PRIVATE_KEY_PATH``
 
   - default: ``/path/to/private_key``
   - The path to the RSA private key file in PEM format, only used if URLCRYPT_USE_RSA_ENCRYPTION is True.

 - ``RUNNING_TESTS``
 
   - default: ``False``
   - Set ``RUNNING_TESTS`` to True when running the urlcrypt tests.

Credits
********
`David Ziegler`_

`Christopher Hesse`_

.. _`David Ziegler`: http://github.com/dziegler
.. _`Christopher Hesse`: http://github.com/cshesse

