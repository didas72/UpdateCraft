from os import environ
from sys import stderr

DEBUG = "DEBUG" in environ

def debug(*args) -> None:
	if not DEBUG:
		return
	print("DEBUG:", *args, file=stderr)

def debug_wait():
	input("DEBUG_WAIT: Press enter to continue")
