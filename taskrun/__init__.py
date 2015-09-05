"""This module provides the entire taskrun system"""

from .Condition import Condition
from .FunctionCondition import FunctionCondition
from .FunctionTask import FunctionTask
from .Observer import Observer
from .ProcessTask import ProcessTask
from .Resource import Resource
from .ResourceManager import ResourceManager
from .Task import Task
from .TaskManager import TaskManager

__version__ = '3.0.0'
