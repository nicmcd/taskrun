# TaskRun

An easy-to-use python package for running tasks with dependencies, conditions,
and resource management. It supports function tasks and process tasks. The
interface is extensible so any custom Task can be implemented. Resource
management consists of generic resources via counters and memory resource
enforcement. Tasks can have conditional execution based on file dependencies,
function conditions, or any other custom condition. Tasks can have other tasks
as dependencies.
