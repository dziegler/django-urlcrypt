from setuptools import setup, find_packages
import urlcrypt
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

README = read('README.rst')

setup(
    name = "django-urlcrypt",
    version = urlcrypt.__version__,
    description = 'Encrypts information in urls, such as login credentials. Useful if you want to send a user a link that logs the user in without leaking their login credentials.',
    long_description = README,
    url = 'http://github.com/dziegler/django-urlcrypt',
    author = 'David Ziegler',
    author_email = 'david.ziegler@gmail.com',
    license = 'BSD',
    zip_safe = False,
    packages = find_packages(),
    include_package_data = True,
    package_data = {'urlcrypt': ['test/test_private_key']},
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
