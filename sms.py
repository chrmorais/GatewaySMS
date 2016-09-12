#!/usr/bin/env python
# -*- coding: utf-8

import sys, traceback, time
from src import main, log

defaults = {}
defaults["email"] = ["email1@dominio", "email2@dominio"]
defaults["ddi"] = "55"
defaults["ddd"] = "47"
defaults["teste"] = False
defaults["provedor"] = "Zenvia"
defaults["zenvia_user"] = "usuario"
defaults["zenvia_password"] = "sEnHa"
defaults["zenvia_confirm_http"] = False
defaults["origem"] = "Nome da origem que aparece no SMS"
defaults["fake_rec"] = 0
defaults["timestamp"] = time.strftime("%Y%m%d%H%M%S", time.gmtime(time.time()))
defaults["daemon"] = False


if len(sys.argv) > 1 and sys.argv[1] == "-t":
	defaults["provedor"] = "Fake"
	defaults["teste"] = True
	defaults["fake_rec"] = 3
	print "MODO TESTE"

if len(sys.argv) > 1 and sys.argv[1] == "-f":
	defaults["teste"] = True


try:
	main.main(defaults)
except Exception:
	exc_type, exc_value, exc_traceback = sys.exc_info()
	lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
	txt = ''.join(line for line in lines)
	log.admin(txt)
	sys.exit(1)
