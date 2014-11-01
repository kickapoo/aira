# Divide Production Settings from Development settings
from .base import *

try:
	from .local import *
except ImportError:
	pass
