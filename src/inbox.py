# -*- coding: utf-8

import sys, os, glob, hashlib, time
from src import log, formato_in, util, defs

def processar():
	for arquivo in glob.glob(os.path.join("INBOX", "*.csv")):
		nomearq = util.nomearq(arquivo)
		dados = file(arquivo).read()
		h1 = hashlib.sha1(dados).hexdigest()

		if defs.get("teste"):
			time.sleep(0.1)
		else:
			time.sleep(60)

		dados = file(arquivo).read()
		h2 = hashlib.sha1(dados).hexdigest()

		if h1 <> h2:
			log.log("Arquivo " + arquivo + " ainda sendo gravado")
			continue

		dados, erro = formato_in.parse(dados)
		if erro:
			log.admin("Arquivo " + arquivo + " com problemas --> %s" % erro)
			util.move(arquivo, "INVALIDO")
			continue
		elif not dados:
			log.admin("Arquivo " + arquivo + " vazio")
			util.move(arquivo, "INVALIDO")
			continue

		log.log("Movendo arquivo " + arquivo + " para a fila 'enviar'")
		util.move(arquivo, "ENVIAR")
