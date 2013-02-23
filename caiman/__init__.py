import os
import logging
import warnings
from boto.ec2 import connect_to_region


try:
    from logging import NullHandler
except ImportError:  # NOQA

    class NullHandler(logging.Handler):  # NOQA
        def emit(self, record):
            pass

# hardcoding to eu-west until we need more regions
REGION = 'eu-west-1'

logger = logging.getLogger(__name__)


def get_name(role, environment):
    return u'soma-{}-{}'.format(environment, role)


def get_running_instances(name, vpc_id=None):
    filters = {'tag-key': name,
               'instance-state-name': 'running',
               'vpc-id': vpc_id}
    if not filters['vpc-id']:
        del filters['vpc-id']
    connection = connect_to_region(REGION)
    reservations = connection.get_all_instances(filters=filters)
    for reservation in reservations:
        for instance in reservation.instances:
            yield instance


class RunningInstances(object):
    """Discover running instances on ec2 by tag or by role."""

    def __init__(self, environment_variable=None):
        """

        If an environment_variable is passed in, instances are discovered with
        an ec2 tag prefixed by 'soma-<environment>-'.  Otherwise, the whole
        ec2 tag is used for discovering instances.

        :param string environment_variable: name of environment variable that
            denotes the current application enviroment (e.g.  demo, production)
        """
        self.environment_variable = environment_variable

    def __call__(self, description):
        return self.get_instances(description)

    def get_instances(self, description):
        """Return generator of discovered ec2 instances

        :param string description: description used to discover instances
        """
        if self.environment_variable:
            try:
                environment = os.environ[self.environment_variable]
            except KeyError:
                raise ValueError('Cannot determine running instances with '
                                 'undefined {} environment variable'
                                 .format(self.environment_variable))
            description = get_name(description, environment)
        return get_running_instances(description)

    def addresses(self, description):
        """
        Return generator of the address of each discovered instance.

        :param string description: description used to discover instances
        """
        return (Ec2Instance(host).address for host in
                self.get_instances(description))

    def first_address(self, description, default=''):
        """
        Return the 1st discovered address.

        :param string description: description used to discover instances
        :param string default: fallback value used when no instances can be found
        :rtype: string
        """
        return next(self.addresses(description), default)


class Ec2Instance(object):
    """Wrapper around a boto ec2instance that adds an address attribute.

    Ec2Instance.address delegates to the 1st available way it can find to
    address the boto ec2instance with the order of preference being:
        * publicIp
        * public_dns_name
        * private_ip_address
    """

    def __init__(self, instance):
        #: wrapped ec2instance
        self.instance = instance
        self._address = None

    @property
    def address(self):
        """Address of wrapped ec2instance"""
        if not self._address:
            attrs = ['publicIp', 'public_dns_name', 'private_ip_address']

            # build up an interable of all attributes that exist and are
            # not just empty strings
            options = (getattr(self.instance, attr, None) for attr in attrs)
            options = (match for match in options if match)

            # only need the 1st value
            self._address = next(options, None)
        return self._address

    def __repr__(self):
        return '{} on {}'.format(repr(self.instance), self.address)


LOGLEVEL = 'DEBUG' if os.environ.get('SOMA_ENVIRONMENT', '') == 'demo' else 'ERROR'
DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(message)s'
        },
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'logsna': {
            'format': '%(levelname)-8s [%(asctime)s] %(name)s +%(lineno)d: %(message)s'
        }
    },
    'handlers': {
        'default': {
            'level': LOGLEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'logsna',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'null': {
            'class': 'caiman.NullHandler',
        }
    },
    'loggers': {
    },
}


def add_remote_logger(remote_logger, logger_name, log_config):
    """Returns log_config after adding a graypy handler

    :param string remote_logger: The ip or hostname of a logger server
    :param string logger_name: The name of logger to which we add the graypy handler
    :param dict log_config: A pre-existing log_config dict to add the handler to
    :rtype: dict
    """
    if remote_logger:
        log_config['handlers']['graypy'] = {
            'class': 'graypy.GELFHandler',
            'host': remote_logger,
            'port': 12201,
        }
        log_config['loggers'][logger_name]['handlers'].append('graypy')
    return log_config

# Deprecated functions. To be deleted once client code that uses them is
# updated.


def get_remote_logger(instances):
    warnings.warn('get_remote_logger is deprecated; please use '
                  'caiman.RunningInstances().first_address("logger") instead')
    winner = next(instances, None)
    if winner:
        winner = Ec2Instance(winner).address
    return winner


def get_running_instance_factory(environment_variable=None):
    """
    Returns an appropriate factory callable for getting running instances.

    If an environment_variable is passed in, instances are discovered with an
    ec2 tag prefixed by 'soma-<environment>-'.  Otherwise, the whole ec2 tag
    is used for discovering instances.
    """
    warnings.warn('get_running_instance_factory is deprecated; '
                  'please use caiman.RunningInstances class instead')
    return RunningInstances(environment_variable)

# Legacy functions. Functions that were (unwisely) added to caiman as they
# were in use somewhere across the soma project. May not be in use any longer


def get_running_indexer_hostnames(name, vpc_id=None):
    # TODO this function is only used in soma-stream/test_indexing.py +48
    # can probably be deleted
    hosts = [i.private_ip_address for i in get_running_indexers(name, vpc_id)]
    logger.debug('Found %d soma-indexers' % len(hosts))
    if not hosts:
        logger.error('No soma-indexers found')
        hosts = ['localhost']
    return hosts


get_running_indexers = get_running_instances
