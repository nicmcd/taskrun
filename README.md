# taskrun

## Summary

An easy-to-use python package for running tasks with dependencies, conditions,
and resource management. It supports function tasks and process tasks. The
interface is extensible so any custom Task can be implemented. Resource
management consists of generic resources via counters and memory resource
enforcement. Tasks can have conditional execution based on file dependencies,
function conditions, or any other custom condition. Tasks can have other tasks
as dependencies.

## Install

Taskrun requires Python 3.4+

### Python package manager (PIP)
Install globally:
```bash
sudo pip3 install git+https://github.com/nicmcd/taskrun.git
```
Install locally:
```bash
pip3 install --user git+https://github.com/nicmcd/taskrun.git
```

### Source installation
Install globally:
```bash
sudo python3 setup.py install
```
Install locally:
```bash
python3 setup.py install --user
```

## Uninstall
Uninstall global installation:
```bash
sudo pip3 uninstall taskrun
```
Uninstall local installation:
```bash
pip3 uninstall taskrun
```

## Test
```bash
make test
````

## Benchmark
```bash
make benchmark
```

## Tutorial
TBD