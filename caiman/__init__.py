import os
import logging
from boto.ec2 import connect_to_region


try:
    from logging import NullHandler
except ImportError:

    class NullHandler(logging.Handler): # NOQA
        def emit(self, record):
            pass

# hardcoding to eu-west until we need more regions
REGION = 'eu-west-1'

logger = logging.getLogger(__name__)


def get_name(role, environment):
    return u'soma-{}-{}'.format(environment, role)


class Config(object):

    @property
    def vpc_id(self):
        vpc_id = os.environ.get('SOMA_VPC_ID', None)
        return vpc_id

config = Config()


def get_running_instances(name, vpc_id=config.vpc_id):
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


get_running_indexers = get_running_instances


def get_running_instance_factory(environment_variable=None):
    """
    Returns an appropriate factory callable for getting running instances.

    If an environment_variable is passed in, instances are discovered with an
    ec2 tag prefixed by 'soma-<environment>-'.  Otherwise, the whole ec2 tag
    is used for discovering instances.
    """
    return RunningInstances(environment_variable)


class RunningInstances(object):

    def __init__(self, environment_variable=None):
        """
        Returns an appropriate factory callable for getting running instances.

        If an environment_variable is passed in, instances are discovered with
        an ec2 tag prefixed by 'soma-<environment>-'.  Otherwise, the whole
        ec2 tag is used for discovering instances.
        """
        self.environment_variable = environment_variable

    def __call__(self, ec2_tag):
        return self.get_instances(ec2_tag)

    def get_instances(self, role):
        if self.environment_variable:
            try:
                environment = os.environ[self.environment_variable]
            except KeyError:
                raise ValueError('Cannot determine running instances with '
                                 'undefined {} environment variable'
                                 .format(self.environment_variable))
            role = get_name(role, environment)
        return get_running_instances(role)

    def addresses(self, ec2_tag):
        return (Ec2Instance(host).address for host in
                self.get_instances(ec2_tag))

    def first_address(self, ec2_tag, default=None):
        return next(self.addresses(ec2_tag), default)


def get_running_indexer_hostnames(name, vpc_id=config.vpc_id):
    hosts = [i.private_ip_address for i in get_running_indexers(name, vpc_id)]
    logger.debug('Found %d soma-indexers' % len(hosts))
    if not hosts:
        logger.error('No soma-indexers found')
        hosts = ['localhost']
    return hosts


class Ec2Instance(object):

    def __init__(self, instance):
        self.instance = instance
        self._address = None

    @property
    def address(self):
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


def get_remote_logger(instances):
    winner = next(instances, None)
    if winner:
        winner = Ec2Instance(winner).address
    return winner


def add_remote_logger(remote_logger, logger_name, log_config):
    if remote_logger:
        log_config['handlers']['graypy'] = {
            'class': 'graypy.GELFHandler',
            'host': remote_logger,
            'port': 12201,
        }
        log_config['loggers'][logger_name]['handlers'].append('graypy')
    return log_config
