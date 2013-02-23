CAIMAN
======

Documentation
*************

The latest version of the caiman docs is always available at
`adaptivelab.github.com/caiman <http://adaptivelab.github.com/caiman>`_


Using caiman
~~~~~~~~~~~~

The main useful feature of caiman is `RunningInstances` which is used for
discovery of running ec2 instances::

    >>> from caiman import RunningInstances

When instantiated without arguments, each method of `RunningInstances` expects
as its sole argument the tag of an ec2 instance::

    >>> running_instances = RunningInstances()

    >>> running_instances.addresses('some-tag-used-on-ec2')
    <generator object <genexpr> at 0x10eca3820>

    >>> [address for address in running_instances.addresses('some-tag-used-on-ec2')]
    [u'ec2-54-246-16-213.eu-west-1.compute.amazonaws.com']

    >>> running_instances.first_address('some-tag-used-on-ec2')
    u'ec2-54-246-16-213.eu-west-1.compute.amazonaws.com'

    >>> running_instances.get_instances('some-tag-used-on-ec2')
    <generator object get_running_instances at 0x10f7574b0>

    >>> [instance for instance in running_instances.get_instances('some-tag-used-on-ec2')]
    [Instance:i-4ae04800]


Alternatively, `RunningInstances` can be instantiated with the name of an
environment variable the value of which will be used to create a tag prefix
meaning that instead of complete tags being required for discovery, roles
alone can be used. This only makes sense with the AdaptiveLab naming
convention and so an explanation of that convention is in order.

Tags are made of three components::

    projectname-environment-role

Where environment could be production, demo, staging, etc. and role could be
database, webserver, logger, etc. So a server used for logging in the
production environment of the globaldomination project would have a tag like::

    globaldomination-production-logger


Using `RunningInstances` with the environment variable and role names looks
almost identical to using it with fully-formed tags::

    >>> import os

    >>> os.environ['an_agreed_upon_variable_name'] = 'demo' # of course environment variables in real systems are not typically set like this

    >>> running_instances = RunningInstances('an_agreed_upon_variable_name')

    >>> running_instances.addresses('database')
    <generator object <genexpr> at 0x10eca1370>

    >>> [address for address in running_instances.addresses('database')]
    [u'ec2-54-246-16-213.eu-west-1.compute.amazonaws.com']

    >>> running_instances.first_address('database')
    u'ec2-54-246-16-213.eu-west-1.compute.amazonaws.com'

    >>> running_instances.get_instances('database')
    <generator object get_running_instances at 0x10f7574b0>

    >>> [instance for instance in running_instances.get_instances('database')]
    [Instance:i-4ae04800]

The only difference in these cases is that instead of having to specify the
full tag name `RunningInstances` automatically converted `database` into
`projectname-demo-database` for us
