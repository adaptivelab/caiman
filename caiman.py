import os
import logging
from boto.ec2 import connect_to_region

# hardcoding to eu-west until we need more regions
REGION = 'eu-west-1'

connection = connect_to_region(REGION)
logger = logging.getLogger(__name__)


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
    reservations = connection.get_all_instances(filters=filters)
    for reservation in reservations:
        for instance in reservation.instances:
            yield instance


get_running_indexers = get_running_instances


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
            attrs = ['publicIp', 'public_dns_name']

            # build up an interable of all attributes that exist and are
            # not just empty strings
            options = (getattr(self.instance, attr, None) for attr in attrs)
            options = (match for match in options if match)

            # only need the 1st value
            self._address = next(options, None)
        return self._address

    def __repr__(self):
        return '{} on {}'.format(repr(self.instance), self.address)
