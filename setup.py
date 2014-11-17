from setuptools import setup, Command
from setuptools.command.test import test as TestCommand
from setuptools.command.install import install as InstallCommand
from setuptools.command.develop import develop as DevelopCommand
import sys
import os
from subprocess import call


def _bower_install():
    print('\n\n-- Installing Client Dependencies (Bower) --\n\n')
    os.system('bower install')
    print('\n\n-- Client Dependencies Installed --\n\n')


class Install(InstallCommand):

    def run(self):
        InstallCommand.run(self)
        _bower_install()


class Develop(DevelopCommand):

    def run(self):
        DevelopCommand.run(self)
        _bower_install()


class PyTest(TestCommand):
    def finalize_options(self):
        os.system('printf "\033c"')
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


class PyDoc(Command):
    description = 'run documentation'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        cwd = os.getcwd()
        os.chdir('tdf/public/docs/')
        call(['make', 'html'])
        os.chdir(cwd)

requires = [
    'pyramid',
    'pyramid_chameleon',
    'sqlalchemy',
    'pymysql',
]

tests_requires = [
    'pytest',
    'webtest',
]

# TODO figure out how to ignore if not in development mode
development_requires = [
    'pyramid_debugtoolbar'
]
requires += development_requires

setup(name='pytdf',
      version='0.0.1',
      packages=['tdf'],
      include_package_data=True,
      install_requires=requires,
      tests_require=tests_requires,
      cmdclass={
          'install': Install,
          'develop': Develop,
          'test': PyTest,
          'document': PyDoc
      },
      entry_points="""\
      [paste.app_factory]
      main = tdf:main
      """)
