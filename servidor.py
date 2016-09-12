#!/usr/bin/env python
# -*- coding: utf-8

import sys, traceback, time
from src import servidor, log

defaults = {}
defaults["email"] = ["email1@dominio", "email2@dominio"]
defaults["teste"] = False
defaults["timestamp"] = time.strftime("%Y%m%d%H%M%S", time.gmtime(time.time()))
defaults["daemon"] = True

try:
	servidor.main(defaults)
except Exception:
	exc_type, exc_value, exc_traceback = sys.exc_info()
	lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
	txt = ''.join(line for line in lines)
	log.admin(txt)
	sys.exit(1)
