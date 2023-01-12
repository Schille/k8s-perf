from pprint import pprint
import json

import kubernetes as k8s
from .runner import BenchmarkRunner


def main():
    k8s.config.load_kube_config()
    runner = BenchmarkRunner()
    try:
        result = runner.run()
    except KeyboardInterrupt:
        print("Cleaning up...")
        cleanup()
    else:
        pprint(result, indent=2)
        with open("results.json", "w") as f:
            json.dump(result, f)


def cleanup():
    k8s.config.load_kube_config()
    runner = BenchmarkRunner()
    runner.cleanup()


if __name__ == "__main__":
    main()
