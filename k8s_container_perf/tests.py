import abc
import re
from typing import List


class Benchmark(abc.ABC):
    @abc.abstractmethod
    def get_command(self) -> List[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_results(self, output: str) -> dict:
        raise NotImplementedError

    def get_resource_limits(self) -> dict:
        return {}

    def get_resource_requests(self) -> dict:
        return {}


class CPUBenchmark(Benchmark):
    def get_command(self, time: int = 60) -> List[str]:
        return ["sysbench", "--test=cpu", f"--time={time}", "run"]

    def get_results(self, output: str) -> dict:
        """
        ...

        Latency (ms):
                 min:                                    1.09
                 avg:                                    1.13
                 max:                                   10.07
                 95th percentile:                        1.32
                 sum:                                 9991.44

        Threads fairness:
            events (avg/stddev):           8866.0000/0.00
            execution time (avg/stddev):   9.9914/0.00
        """
        total_time = re.findall(r"total time:\s*(.*)\s", output)[0]
        total_events = re.findall(r"total number of events:\s*(.*)\s", output)[0]
        eps = re.findall(r"events per second:\s*(.*)\s", output)[0]
        latency_min = re.findall(r"min:\s*(.*)\s", output)[0]
        latency_avg = re.findall(r"avg:\s*(.*)\s", output)[0]
        latency_max = re.findall(r"max:\s*(.*)\s", output)[0]
        latency_95th = re.findall(r"95th percentile:\s*(.*)\s", output)[0]
        latency_sum = re.findall(r"sum:\s*(.*)\s", output)[0]
        return {
            "events_per_second": eps,
            "total_time": total_time,
            "total_events": total_events,
            "latency_min": latency_min,
            "latency_avg": latency_avg,
            "latency_max": latency_max,
            "latency_95th": latency_95th,
            "latency_sum": latency_sum,
            "command": " ".join(self.get_command()),
        }


class MemoryBenchmark(Benchmark):
    def get_command(self, size: str = "500G") -> List[str]:
        return ["sysbench", "--test=memory", f"--memory-total-size={size}", "run"]

    def get_results(self, output: str) -> dict:
        """
        ...

        Total operations: 35343044 (3533507.23 per second)

        34514.69 MiB transferred (3450.69 MiB/sec)


        General statistics:
            total time:                          10.0002s
            total number of events:              35343044

        Latency (ms):
                min:                                    0.00
                avg:                                    0.00
                max:                                    4.06
                95th percentile:                        0.00
                sum:                                 4607.93

        Threads fairness:
            events (avg/stddev):           35343044.0000/0.00
            execution time (avg/stddev):   4.6079/0.00
        """
        total_time = re.findall(r"total time:\s*(.*)\s", output)[0]
        total_events = re.findall(r"total number of events:\s*(.*)\s", output)[0]
        transferred = re.findall(r"\s*(.*)\stransferred", output)[0]
        write_per_sec = re.findall(r"transferred\s*\((.*)\)", output)[0]
        latency_min = re.findall(r"min:\s*(.*)\s", output)[0]
        latency_avg = re.findall(r"avg:\s*(.*)\s", output)[0]
        latency_max = re.findall(r"max:\s*(.*)\s", output)[0]
        latency_95th = re.findall(r"95th percentile:\s*(.*)\s", output)[0]
        latency_sum = re.findall(r"sum:\s*(.*)\s", output)[0]
        return {
            "total_time": total_time,
            "total_events": total_events,
            "transferred": transferred,
            "write_per_sec": write_per_sec,
            "latency_min": latency_min,
            "latency_avg": latency_avg,
            "latency_max": latency_max,
            "latency_95th": latency_95th,
            "latency_sum": latency_sum,
            "command": " ".join(self.get_command()),
        }


class FileIOBenchmark(Benchmark):
    def get_command(self, size: str = "5G", num_files: int = 5, time: int = 100) -> List[str]:
        return f"sysbench --test=fileio --file-num={num_files} --file-total-size={size} prepare && sysbench " \
               f"--test=fileio --file-total-size={size} --file-num={num_files} --file-test-mode=rndrw --time={time} " \
               "--max-requests=0 run".split()

    def get_results(self, output: str) -> dict:
        """
        ...

        File operations:
            reads/s:                      238.16
            writes/s:                     158.77
            fsyncs/s:                     19.89

        Throughput:
            read, MiB/s:                  3.72
            written, MiB/s:               2.48

        General statistics:
            total time:                          100.0287s
            total number of events:              41690

        Latency (ms):
                min:                                    0.00
                avg:                                    2.40
                max:                                  103.12
                95th percentile:                       18.28
                sum:                                99941.66

        Threads fairness:
            events (avg/stddev):           41690.0000/0.00
            execution time (avg/stddev):   99.9417/0.00
        """
        throughput_read = re.findall(r"read, MiB/s:\s*(.*)\s", output)[0]
        throughput_write = re.findall(r"written, MiB/s:\s*(.*)\s", output)[0]
        fileops_read = re.findall(r"reads/s:\s*(.*)\s", output)[0]
        fileops_write = re.findall(r"writes/s:\s*(.*)\s", output)[0]
        fileops_fsync = re.findall(r"fsyncs/s:\s*(.*)\s", output)[0]
        total_time = re.findall(r"total time:\s*(.*)\s", output)[0]
        total_events = re.findall(r"total number of events:\s*(.*)\s", output)[0]
        latency_min = re.findall(r"min:\s*(.*)\s", output)[0]
        latency_avg = re.findall(r"avg:\s*(.*)\s", output)[0]
        latency_max = re.findall(r"max:\s*(.*)\s", output)[0]
        latency_sum = re.findall(r"sum:\s*(.*)\s", output)[0]
        latency_95th = re.findall(r"95th percentile:\s*(.*)\s", output)[0]
        return {
            "total_time": total_time,
            "total_events": total_events,
            "latency_min": latency_min,
            "latency_avg": latency_avg,
            "latency_max": latency_max,
            "latency_sum": latency_sum,
            "latency_95th": latency_95th,
            "throughput_read": throughput_read,
            "throughput_write": throughput_write,
            "fileops_read": fileops_read,
            "fileops_write": fileops_write,
            "fileops_fsync": fileops_fsync,
            "command": " ".join(self.get_command()),
        }
