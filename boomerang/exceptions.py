# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class BoomerangFailedTask(Exception):
    """
    Raising this in a Boomerang task halts execution and updates the Job's
    state to FAILED, but will not re-raise an exception afterwards.
    """
    pass
