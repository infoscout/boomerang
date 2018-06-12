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
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'boomerang',
            ),
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
