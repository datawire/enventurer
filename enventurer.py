#!/usr/bin/env python

# Copyright 2016 Datawire. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import boto3
import logging
import re
import requests
import os

"""
Inspects EC2 metadata and writes Key/Value pairs to a file that can be sourced by other programs as a means of providing
environment variables. This can be very handy when used as a systemd service that runs before any app or server runs.
"""

__author__ = "Philip Lombardi"
__copyright__ = "Copyright 2016 Datawire"
__license__ = "Apache 2.0"
__maintainer__ = "Philip Lombardi"
__email__ = "plombardi@datawire.io"

EC2_METADATA_URL = "http://169.254.169.254/latest/meta-data/"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(module)s - %(message)s")
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

logger = logging.getLogger('enventurer.py')

ec2 = None


def write_environment_variables(variables):
    content = "\n".join(['{}={}'.format(k.upper(), v) for (k, v) in variables.items()])

    try:
        os.makedirs('/etc/datawire')
    except OSError:
        if not os.path.isdir('/etc/datawire'):
            raise

    with open('/etc/datawire/environment', 'a+') as f:
        logger.info("Writing environment variables to filesystem")
        f.write(content)

    os.chmod('/etc/datawire/environment', 0644)


def query_tags(resource_ids):
    result = {}
    tags = ec2.describe_tags(Filters=[{'Name': 'resource-id', 'Values': resource_ids}]).get('Tags', [])
    logger.info("Found %s tags attached to %s resources", len(tags), len(resource_ids))

    for tag in tags:
        name = "{}_{}".format(tag['ResourceType'], tag['Key'])
        value = "'{}'".format(tag['Value'])

        # Just ignore the AWS tags to avoid people using AWS implementation details to configure services.
        if not name.startswith("aws:"):
            name = normalize_tag_name(name)
            result[name] = value

    return result


def normalize_tag_name(name):
    """ Normalize an EC2 resource tag to be compatible with shell environment variables. Basically it means the the
    following regex must be followed: [a-Z][a-Z0-9_]*. This function is not meant to handle all possible corner cases so
    try not to be stupid with tag naming.

    :param name: the tag name
    :return: a normalized version of the tag name
    """
    result = name

    if name[0].isdigit():
        result = "_" + name

    result = re.sub('[^0-9a-zA-Z_]+', '_', result)

    return result.upper()


def query_metadata(prop):
    response = requests.get("{}/{}".format(EC2_METADATA_URL, prop))
    result = response.text
    logger.info("Queried metadata server for '%s' found '%s'", prop, result)
    return result


def main():
    region = query_metadata('placement/availability-zone').lower().rstrip("abcdefghijklmnopqrstuvwxyz")

    global ec2
    ec2 = boto3.client('ec2', region_name=region)

    instance_id = query_metadata('instance-id')
    image_id = query_metadata('ami-id')

    tags = query_tags([instance_id, image_id])
    write_environment_variables(tags)


if __name__ == "__main__":
    main()




