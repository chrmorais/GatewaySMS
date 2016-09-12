# -*- coding: utf-8

from src import defs, log

def consistir(fone_orig):
	# Remove todos os caracteres especiais, adiciona
	# DDD e DDI se parece faltar, escolhe o melhor gateway
	# ou operadora para envio de SMS ao número em questão, 
	# e reporta erro para números flagrantemente errados

	# TODO: este algoritmo não consegue lidar com números de
	# qualquer lugar do mundo, pois diferentes países têm
	# diferentes comprimentos de número, DDD diferente ou
	# inexistente, etc. O algoritmo abaixo só é garantido
	# para telefones celulares brasileiros com 8 ou 9 dígitos. 

	# Para lidar com números internacionais, o algoritmo teria
	# de conhecer de forma bastante profunda os planos de 
	# numeração de todos os países, ou o cadastro que gera os
	# arquivos CSV deveria conter o prefixo internacional.

	fone = ""
	err = None
	provedor = None

	for i in range(0, len(fone_orig)):
		c = fone_orig[i]
		if c >= '0' and c <= '9':
			fone += c

	# Remove prefixo zero de DDD ou DDI
	while len(fone) > 0 and fone[0] == '0':
		fone = fone[1:]

	if len(fone) < 8:
		err = "Telefone '%s' muito curto para ser válido" % fone
	elif len(fone) > 15:
		err = "Telefone %s muito longo para ser válido" % fone
	elif len(fone) <= 9:
		fone = defs.get("ddi") + defs.get("ddd") + fone
	elif len(fone) <= 11:
		fone = defs.get("ddi") + fone

	# No momento não escolhe operadora
	# TODO
	provedor = defs.get("provedor")

	if err:
		log.log(err)	

	return fone, provedor, err
