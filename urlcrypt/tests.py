from django import template
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from test_utils.testcase import TestCase
from urlcrypt import lib as urlcrypt
from urlcrypt.conf import URLCRYPT_LOGIN_URL

class UrlCryptTests(TestCase):
    
    def setUp(self):
        super(UrlCryptTests, self).setUp()
        self.test_user = User.objects.create_user('test', 'test@malinator.com', 'test')
    
    def test_token_encoding(self):
        message = {
            'url': '/users/following', 
            'user_id': '12345'
        }

        token = urlcrypt.encode_token(message['user_id'], message['url'])
        decoded_message = urlcrypt.decode_token(token,('user_id', 'url', 'timestamp'))
        for key, val in message.iteritems():
            assert val == decoded_message[key]
    
    def test_login_token(self):
        token = urlcrypt.generate_login_token(self.test_user, u'/users/following')
        data = urlcrypt.decode_login_token(token)
        self.assertEquals(data['user_id'], self.test_user.id)
        self.assertEquals(data['url'], u'/users/following')
    
    def test_login_token_failed_hax0r(self):
        fake_token = 'asdf;lhasdfdso'
        response = self.client.get(reverse('urlcrypt_redirect', args=(fake_token,)))
        self.assertRedirects(response, URLCRYPT_LOGIN_URL)
        
        fake_token = urlcrypt.encode_token(str(self.test_user.id), str('asdf;ljasdf'), reverse('urlcrypt_test_view'))
        response = self.client.get(reverse('urlcrypt_redirect', args=(fake_token,)))
        self.assertRedirects(response, URLCRYPT_LOGIN_URL)
            
    def assert_login_url(self, encoded_url, expected_url):
        response = self.client.get(expected_url)
        self.assertEquals(response.status_code, 302)
        response = self.client.get(encoded_url)
        self.assertRedirects(response, expected_url)
        response = self.client.get(expected_url)
        self.assertEquals(response.status_code, 200)
        
    def test_url_encoded_template_tag(self):
        
        text = """
        {% load urlcrypt_tags %}
        {% encoded_url test_user urlcrypt_test_view %}
        """
        t = template.Template(text)
        c = template.Context({'test_user': self.test_user})
        encoded_url = t.render(c).strip()
        self.assert_login_url(encoded_url, reverse('urlcrypt_test_view'))
    
    def test_url_encoded_template_tag_with_args(self):
        
        text = """
        {% load urlcrypt_tags %}
        {% encoded_url test_user urlcrypt_test_view_username test_user.username %}
        """
        t = template.Template(text)
        c = template.Context({'test_user': self.test_user})
        encoded_url = t.render(c).strip()
        self.assert_login_url(encoded_url, reverse('urlcrypt_test_view_username', args=(self.test_user.username,)))
    
    def test_encode_url_string_template_tag(self):
        text = """
        {% load urlcrypt_tags %}
        {% encode_url_string test_user some_url %}
        """
        some_url = 'http://testserver%s' % reverse('urlcrypt_test_view_username', args=(self.test_user.username,))
        t = template.Template(text)
        c = template.Context({'test_user': self.test_user, 'some_url': some_url})
        encoded_url = t.render(c).strip()
        self.assert_login_url(encoded_url, reverse('urlcrypt_test_view_username', args=(self.test_user.username,)))
     