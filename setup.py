from setuptools import Command, find_packages, setup


with open('VERSION', 'r') as f:
    version = f.read().strip()


class TestCommand(Command):

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import django
        from django.conf import settings
        from django.core.management import call_command

        settings.configure(
            DATABASES={
                'default': {
                    'NAME': ':memory:',
                    'ENGINE': 'django.db.backends.sqlite3',
                },
            },
            INSTALLED_APPS=(
                'django.contrib.admin',
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'boomerang',
            ),
            TEMPLATES=[
                {
                    'BACKEND': 'django.template.backends.django.DjangoTemplates',
                    'APP_DIRS': True,
                    'OPTIONS': {
                        'context_processors': [
                            'django.contrib.auth.context_processors.auth',
                            'django.contrib.messages.context_processors.messages',
                        ],
                    },
                },
            ],
            MIDDLEWARE=(
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
            ),
            MIDDLEWARE_CLASSES=(
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
            ),  # Django < 1.10
            ROOT_URLCONF='boomerang.tests.urls',
            CELERY_ALWAYS_EAGER=True,
            CELERY_TASK_ALWAYS_EAGER=True
        )
        django.setup()
        call_command('test', 'boomerang')


setup(
    name='boomerang',
    packages=find_packages(),
    include_package_data=True,
    description='Django app to asynchronously process tasks',
    url='http://github.com/infoscout/boomerang',
    version=version,
    install_requires=[
        'Django >= 1.8, < 2.0a0',
        'celery >= 3.0',
    ],
    cmdclass={'test': TestCommand}
)
