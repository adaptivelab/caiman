import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    name='caiman',
    version='1.0',
    long_description='Simple helpers for aws',
    include_package_data=True,
    zip_safe=False,
    tests_require=['fudge==1.0.3', 'pytest==2.3.4'],
    cmdclass={'test': PyTest},
)
