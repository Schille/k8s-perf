from typing import List
import kubernetes as k8s

from .runner import BenchmarkRunner
from .tests import Benchmark


def get_pod_object(
    name: str, test: Benchmark, runner: BenchmarkRunner
) -> k8s.client.V1Pod:
    sysbench_container = k8s.client.V1Container(
        name="sysbench",
        image=runner.SYSBENCH_IMAGE,
        image_pull_policy="IfNotPresent",
        command=["bash", "-c"],
        args=[" ".join(test.get_command())],
        resources=k8s.client.V1ResourceRequirements(
            requests=test.get_resource_requests(),
            limits=test.get_resource_limits(),
        ),
    )

    spec = k8s.client.V1PodSpec(containers=[sysbench_container], restart_policy="Never")

    _labels = runner.LABELS.copy()
    _labels.update({"sysbench-test": test.__class__.__name__})

    pod = k8s.client.V1Pod(
        metadata=k8s.client.V1ObjectMeta(
            name=name, namespace=runner.NAMESPACE, labels=_labels
        ),
        spec=spec,
    )
    return pod
