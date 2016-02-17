"""
Raising this in a Boomerang task halts execution and updates the Job's
state to FAILED, but will not re-raise an exception afterwards.
"""

class BoomerangFailedTask(Exception):
	pass