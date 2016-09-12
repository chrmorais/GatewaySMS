# -*- coding: utf-8

defaults = None

def read(defs):
	global defaults
	defaults = defs

def get(name):
	return defaults[name]
