# -*- coding: utf-8

import sys, os, glob, hashlib, time
from src import log, util

def nomearq(lote):
	# Nome de arquivo relativo a um nome de lote
	# (O nome do lote é o nome original do arquivo postado em INBOX)
	return os.path.join("ENVIADAS", lote + ".env")

def dicionario(lote):
	# Obtém lista de IDs já enviados (não necessariamente confirmados)
	# Nós confiamos no formato deste arquivo pois é nosso próprio programa
	# que gera o mesmo
	dic = {}
	arquivo = nomearq(lote)
	if not os.path.exists(arquivo):
		log.log("Nenhuma msg enviada de %s" % lote)
		return dic 
	log.log("Enviadas: abrindo arquivo %s" % arquivo)
	alista = open(arquivo).readlines()
	alista = [ registro.strip().split(",") for registro in alista ]

	for registro in alista:
		if len(registro) < 3:
			log.admin("Registro corrompido em %s: %s" % (arquivo, str(registro)))
			continue
		reg = {}
		reg["hora"] = registro[1]
		reg["status"] = registro[2]
		dic[registro[0]] = reg
	
	return dic

def remover(lote):
	# Move o recibo de envio para o lixo de forma segura
	arquivo = nomearq(lote)
	util.move(arquivo, "LIXO")

def registrar(lote, ID, status):
	# Registra um envio de forma segura
	arquivo = nomearq(lote)
	util.gravaseguro(arquivo, "%s,%f,%d\n" % (ID, time.time(), status))

