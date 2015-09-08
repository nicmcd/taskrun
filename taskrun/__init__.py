"""This module provides the entire taskrun system"""

from .Condition import Condition
from .FailureMode import FailureMode
from .FileChangedDatabase import FileChangedDatabase
from .FileCondition import FileCondition
from .FunctionCondition import FunctionCondition
from .FunctionTask import FunctionTask
from .NopTask import NopTask
from .Observer import Observer
from .ProcessTask import ProcessTask
from .Resource import Resource
from .ResourceManager import ResourceManager
from .Task import Task
from .TaskManager import TaskManager
from .VerboseObserver import VerboseObserver

__version__ = '3.0.0'
