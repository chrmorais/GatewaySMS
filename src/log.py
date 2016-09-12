# -*- coding: utf-8

import os, datetime, subprocess

from src import defs

def nome_log():
	hoje = datetime.date.today()
	return "log-" + hoje.isoformat() + ".log"

fnome = ""
f = None

def arquivo():
	global fnome, f
	if nome_log() == fnome:
		return f
	fnome = nome_log()
	f = open(os.path.join("LOG", fnome), "a")
	return f

def fmt(msg):
	return datetime.datetime.today().isoformat() + " " + msg

def log(msg):
	msg = fmt(msg)
	print msg
	arquivo().write(msg)
	arquivo().write("\n")
	arquivo().flush()

def admin(msg):
	msg = ">>>>> " + msg
	log(msg)

	if defs.get("teste"):
		return

	subject = "SMS gateway: aviso de problema"
	recipients = defs.get("email")
	if type(recipients) is not list:
		recipients = [ recipients ]

	for rec in recipients:
		try:
			process = subprocess.Popen(
				['mail', '-s', subject, rec],
				stdin=subprocess.PIPE)
		except Exception, error:
			log(">>>>>>>>> Não pode enviar e-mail ao admin: " + str(error));
			return

		process.communicate(msg)
