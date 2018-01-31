from oslo_log import log as logging
from oslo_utils import timeutils

from nova.compute.monitors import base
import nova.conf
from nova import exception
from nova.i18n import _LE

CONF = nova.conf.CONF
LOG = logging.getLogger(__name__)


class Monitor(base.VmwareMonitorBase):
    def __init__(self, resource_tracker):
        super(Monitor, self).__init__(resource_tracker)
        self.source = CONF.compute_driver
        self.driver = resource_tracker.driver
        self._data = {}

    def get_metrics(self):
        metrics = []
        self._update_data()
        for name in self.get_metric_names():
            metrics.append((name, self._data[name], self._data["timestamp"]))
        return metrics

    def _update_data(self):
        self._data = {}
        self._data["timestamp"] = timeutils.utcnow()
        try:
            metric_stats = self.driver.get_cluster_metrics()
            self._data['storage.percent.usage'] = metric_stats['datastore_percent']
            self._data['storage.total'] = metric_stats['datastore_total']
            self._data['storage.used'] = metric_stats['datastore_used']
            self._data['storage.free'] = metric_stats['datastore_free']
            self._data['cpu.total'] = metric_stats['cpu_total']
            self._data['cpu.used'] = metric_stats['cpu_used']
            self._data['cpu.free'] = metric_stats['cpu_free']
            self._data['cpu.percent.used'] = metric_stats['cpu_percent']
            self._data['memory.total'] = metric_stats['memory_total']
            self._data['memory.used'] = metric_stats['memory_used']
            self._data['memory.free'] = metric_stats['memory_free']
            self._data['memory.percent'] = metric_stats['memory_percent']

            LOG.info("Cluster metrics: %s", self._data)


        except (NotImplementedError, TypeError, KeyError):
            LOG.exception(_LE("Not all properties needed are implemented "
                              "in the compute driver"))
            raise exception.ResourceMonitorError(
                monitor=self.__class__.__name__)
