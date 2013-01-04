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
        if not vpc_id:
            vpc_id = 111
        return vpc_id

config = Config()


def get_running_indexers(name, vpc_id=config.vpc_id):
    filters = {'tag-key': name,
               'instance-state-name': 'running',
               'vpc-id': vpc_id}
    reservations = connection.get_all_instances(filters=filters)
    for reservation in reservations:
        for instance in reservation.instances:
            yield instance


get_running_instances = get_running_indexers


def get_running_indexer_hostnames(name, vpc_id=config.vpc_id):
    hosts = [i.private_ip_address for i in get_running_indexers(name, vpc_id)]
    logger.debug('Found %d soma-indexers' % len(hosts))
    if not hosts:
        logger.error('No soma-indexers found')
        hosts = ['localhost']
    return hosts
