from django import template
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.template.defaulttags import URLNode

from urlcrypt.conf import RUNNING_TESTS
from urlcrypt.lib import generate_login_token

register = template.Library()

class EncodedURLNode(URLNode):
    
    def __init__(self, user, *args, **kwargs):
        self.user = template.Variable(user)
        super(EncodedURLNode, self).__init__(*args, **kwargs)
    
    def render(self, context):
        url = super(EncodedURLNode, self).render(context)
        if self.asvar:
            url = context[self.asvar]
        user = self.user.resolve(context)
        token = generate_login_token(user, url)
        crypt_url = reverse('urlcrypt_redirect', args=(token,))
        if self.asvar:
            context[self.asvar] = crypt_url
            return ''
        return crypt_url

@register.tag
def encoded_url(parser, token):
    bits = token.split_contents()
    if len(bits) < 3:
        raise template.TemplateSyntaxError("'%s' takes at least two arguments"
                                  " (path to a view)" % bits[0])
    user = bits[1]
    viewname = bits[2]
    args = []
    kwargs = {}
    asvar = None

    if len(bits) > 3:
        bits = iter(bits[3:])
        for bit in bits:
            if bit == 'as':
                asvar = bits.next()
                break
            else:
                for arg in bit.split(","):
                    if '=' in arg:
                        k, v = arg.split('=', 1)
                        k = k.strip()
                        kwargs[k] = parser.compile_filter(v)
                    elif arg:
                        args.append(parser.compile_filter(arg))
    return EncodedURLNode(user, viewname, args, kwargs, asvar)

@register.simple_tag
def encode_url_string(user, url):
    if RUNNING_TESTS:
        domain = 'testserver'
    else:
        domain = Site.objects.get_current().domain
    protocol, suffix = url.split("://%s" % domain)
    token = generate_login_token(user, suffix)
    return "%s://%s" % (protocol, reverse('urlcrypt_redirect', args=(token,)))
