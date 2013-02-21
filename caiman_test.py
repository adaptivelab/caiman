import os
import caiman
import fudge
import pytest


class TestRunningInstance(object):

    @fudge.patch('caiman.get_running_instances')
    def test_can_set_a_specific_ec2_tag_instead_of_role(self, get_running_instances):

        (get_running_instances
         .expects_call()
         .with_args('my_specific_ec2_tag')
         .returns(iter(range(5))))

        running_instances = caiman.RunningInstances()
        result = running_instances('my_specific_ec2_tag')
        assert list(result) == [0, 1, 2, 3, 4]

    @fudge.patch('caiman.get_running_instances')
    def test_returns_callable(self, get_running_instances):
        """returns callable

        get_running_instance_factory returns a callable that calculates a
        name/tag and then proxies to get_running_instance"""
        os.environ['some_var'] = '200'

        (get_running_instances
         .expects_call()
         .with_args('soma-200-break')
         .returns(iter(range(5))))

        running_instances = caiman.RunningInstances('some_var')
        result = running_instances('break')
        assert list(result) == [0, 1, 2, 3, 4]

    @fudge.patch('caiman.get_running_instances')
    def test_addresses_returns_addresses(self, get_running_instances):
        """.addresses returns addresses"""
        os.environ['test_45'] = u'indexer'

        public = type('public', (object, ), {'publicIp': 11})
        dns = type('dns', (object, ), {'public_dns_name': 22})
        response = public, dns

        (get_running_instances
         .expects_call()
         .with_args('soma-indexer-purpose')
         .returns(iter(response)))

        running_instances = caiman.RunningInstances('test_45')
        result = running_instances.addresses('purpose')
        assert list(result) == [11, 22]

    @fudge.patch('caiman.get_running_instances')
    def test_1st_address_returns_single_address(self, get_running_instances):
        """.first_address returns single address"""

        os.environ['test_45'] = u'indexer'

        public = type('public', (object, ), {'publicIp': '44.55'})
        dns = type('dns', (object, ), {'public_dns_name': 22})
        response = public, dns

        (get_running_instances
         .expects_call()
         .with_args('soma-indexer-purpose')
         .returns(iter(response)))

        running_instances = caiman.RunningInstances('test_45')
        assert running_instances.first_address('purpose') == '44.55'

    @fudge.patch('caiman.get_running_instances')
    def test_1st_address_handles_no_instances(self, get_running_instances):
        """.first_address returns single address"""

        os.environ['variable_name'] = u'indexer'

        (get_running_instances
         .expects_call()
         .with_args('soma-indexer-surprise')
         .returns(iter([])))

        running_instances = caiman.RunningInstances('variable_name')
        assert running_instances.first_address('surprise') == ''

    @fudge.patch('caiman.get_running_instances')
    def test_raises_valueerror_w_nonexistant_envvar(self, get_instances):
        """raises ValueError if instantiated with non-existant env var"""
        running_instances = caiman.RunningInstances('non-existant')
        with pytest.raises(ValueError):
            running_instances('doomed')


class TestGetRunningInstances(object):

    @fudge.patch('caiman.connect_to_region')
    def test_with_reservations(self, connect_to_region):

        instances = [100, 200, 300]
        reservations = [fudge.Fake('reservation').has_attr(instances=instances)]
        connection = (fudge.Fake('connection')
                      .expects('get_all_instances')
                      .returns(reservations))
        connect_to_region.expects_call().with_args(caiman.REGION).returns(connection)
        instances = list(caiman.get_running_instances('n/a'))
        assert instances == [100, 200, 300]

    @fudge.patch('caiman.connect_to_region')
    def test_no_reservations(self, connect_to_region):

        reservations = []
        connection = (fudge.Fake('connection')
                      .expects('get_all_instances')
                      .returns(reservations))
        connect_to_region.expects_call().with_args(caiman.REGION).returns(connection)
        instances = list(caiman.get_running_instances('n/a'))
        assert instances == []


class TestAddRemoteLogger(object):

    def test_adds_graypy_handler_to_config(self):
        remote_address = '10.44.22.241'
        logger_name = 'some_logger_name'

        log_config = {
            'handlers': {},
            'loggers': {
                logger_name: {'handlers': []}
            }
        }
        updated_config = caiman.add_remote_logger(remote_address,
                                                  logger_name,
                                                  log_config)
        assert updated_config['handlers']['graypy']['host'] == remote_address
