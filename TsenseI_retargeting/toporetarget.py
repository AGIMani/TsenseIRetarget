"""Compatibility import for the former solver module name.

Both module paths resolve to the same object so existing integrations that
patch solver internals continue to affect the implementation used at runtime.
"""
import sys

from . import tsensei_retarget as _implementation

sys.modules[__name__] = _implementation
