# -*- coding: utf-8

import os, shutil
from . import log

def nomearq(arquivo):
	# Obtém o nome de base do arquivo de forma portável
	return os.path.split(arquivo)[-1]

def move(arquivo, pasta):
	# Move um arquivo de forma segura, sem sobrepor um
	# arquivo de mesmo nome já existente na pasta de destino
	dest = nomearq(arquivo)
	fulldest = os.path.join(pasta, dest)
	i = 0
	while os.path.exists(fulldest):
		i += 1
		fulldest = os.path.join(pasta, dest + (".%d" % i))
	shutil.move(arquivo, fulldest)
	log.log("Movido arquivo %s -> %s" % (arquivo, fulldest))

def gravaseguro(arq, msg):
	# Adiciona dados a um arquivo de forma segura
	# (Dados não serão perdidos nem gravados pela metade)
	f = open(arq, "a")
	f.write(msg)
	f.flush()
	os.fsync(f.fileno())
	f.close()
