
from __future__ import absolute_import

from . import option_list
import origae.device_query


option_list['gpu_list'] = ','.join([str(x) for x in xrange(len(origae.device_query.get_devices()))])
