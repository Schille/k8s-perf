# Kubernetes Sysbench
A tool to run [sysbench](https://github.com/akopytov/sysbench) in Kubernetes and collect the performance results.

## Requirements
* python
* poetry

## Run it

To start the benchmark, run `poetry run benchmark`.
In case something happens, you can clean up the cluster with `poetry run cleanup`.

