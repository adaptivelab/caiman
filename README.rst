CAIMAN
======

Example usage
~~~~~~~~~~~~~

::
    >>> from caiman import RunningInstances
    >>> running_instances = RunningInstances()
    >>> running_instances.addresses('some-tag-used-on-ec2')
    <generator object <genexpr> at 0x10eca3820>
    >>> [address for address in running_instances.addresses('some-tag-used-on-ec2')]
    [u'ec2-54-246-16-213.eu-west-1.compute.amazonaws.com']
    >>> running_instances.first_address('some-tag-used-on-ec2')
    u'ec2-54-246-16-213.eu-west-1.compute.amazonaws.com'
    >>> running_instances.get_instances('some-tag-used-on-ec2')
    <generator object get_running_instances at 0x10f7574b0>
    >>> [instance for instance in running_instances.get_instances('soma-production-db')]
    [Instance:i-4ae04800]

