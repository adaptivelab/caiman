import caiman
import fudge


class TestGetRunningInstanceFactory(object):

    @fudge.patch('caiman.get_running_instances')
    def test_returns_callable(self, get_running_instances):
        """returns callable

        get_running_instance_factory returns a callable that calculates a
        name/tag and then proxies to get_running_instance"""
        import os
        os.environ = {'some_var': 200}

        (get_running_instances
         .expects_call()
         .with_args('soma-200-break')
         .returns(iter(range(5))))

        getter = caiman.get_running_instance_factory('some_var')
        result = getter('break')
        assert list(result) == [0, 1, 2, 3, 4]

    @fudge.patch('caiman.get_running_instances')
    def test_addresses_returns_addresses(self, get_running_instances):
        """.addresses returns addresses"""
        import os
        os.environ = {'test_45': u'indexer'}

        public = type('public', (object, ), {'publicIp': 11})
        dns = type('dns', (object, ), {'public_dns_name': 22})
        response = public, dns

        (get_running_instances
         .expects_call()
         .with_args('soma-indexer-purpose')
         .returns(iter(response)))

        getter = caiman.get_running_instance_factory('test_45')
        result = getter.addresses('purpose')
        assert list(result) == [11, 22]
