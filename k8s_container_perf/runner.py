from pprint import pprint
import kubernetes as k8s

from .tests import CPUBenchmark, MemoryBenchmark, FileIOBenchmark


class BenchmarkRunner:
    SYSBENCH_IMAGE = "severalnines/sysbench"
    NAMESPACE = "default"
    LABELS = {"sysbench-runner": "true"}

    BENCHMARKS = {"cpu": CPUBenchmark(), "memory": MemoryBenchmark(), "fileio": FileIOBenchmark()}

    def cleanup(self):
        core_api = k8s.client.CoreV1Api()
        pods = core_api.list_namespaced_pod(
            namespace=self.NAMESPACE, label_selector="sysbench-runner=true"
        )
        for pod in pods.items:
            core_api.delete_namespaced_pod(
                namespace=self.NAMESPACE, name=pod.metadata.name
            )

    def run(self) -> dict:
        results = {}
        from .utils import get_pod_object

        core_api = k8s.client.CoreV1Api()
        watch = k8s.watch.Watch()

        for name, test in self.BENCHMARKS.items():
            pod_for_test = get_pod_object(f"sysbench-{name}", test, self)
            pod = core_api.create_namespaced_pod(
                namespace=self.NAMESPACE, body=pod_for_test
            )
            print(f"Now running test '{name}': ")
            for event in watch.stream(
                func=core_api.list_namespaced_pod,
                namespace=self.NAMESPACE,
                label_selector=f"sysbench-test={test.__class__.__name__}",
            ):
                if event["type"] == "DELETED":
                    print(f"{name} deleted before it started")
                    watch.stop()
                print(event["object"].status.phase)
                if event["object"].status.phase == "Succeeded":
                    watch.stop()
            # extract output
            _i = 0
            while _i <= 10:
                try:
                    _output = core_api.read_namespaced_pod_log(
                        name=pod_for_test.metadata.name, namespace=self.NAMESPACE
                    )
                except Exception:
                    _i += 1
                else:
                    break
            try:
                results[name] = test.get_results(_output)
            except Exception as e:
                print(e)
            core_api.delete_namespaced_pod(
                namespace=self.NAMESPACE, name=pod_for_test.metadata.name
            )
        return results
