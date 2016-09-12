# -*- coding: utf-8

import sys, os, glob, hashlib
from src import log, util, enviadas, const, formato_in, confirmacao, recepcao


def dicionarizar(lista):
	dic = {}
	for registro in lista:
		dic[registro["id"]] = registro
	return dic


def processar(modulo_gateway):
	for arquivo in glob.glob(os.path.join("ENVIAR", "*.csv*")):
		processa_lote(arquivo, modulo_gateway)


def registrar(lote, ID, status, provedor):
	# Registra o status de envido da mensagem, nos arquivos de
	# log na pasta ENVIADAS/ e também em CONFIRMAR/ se o status
	# é de sucesso.
	enviadas.registrar(lote, ID, status)
	if status == const.STATUS_ENVIADO:
		confirmacao.registrar(lote, ID, provedor)
	else:
		# O status de falha vai direto para OUTBOX, sem esperar confirmação
		recepcao.registrar_recibo(ID, status)


def processa_lote(arq_lote, modulo_gateway):
	lote = util.nomearq(arq_lote)
	conteudo = file(arq_lote).read()
	conteudo, erro = formato_in.parse(conteudo)
	if erro:
		log.admin("Enviar: arquivo " + arq_lote + " com problemas --> %s" % erro)
		util.move(arq_lote, "INVALIDO")
		return

	conteudo = dicionarizar(conteudo)
	env = enviadas.dicionario(lote)

	# Remove do lote o que já foi enviado
	for ID in env.keys():
		if ID in conteudo:
			del conteudo[ID]

	if len(conteudo.keys()) <= 0:
		# Tudo já foi enviado, ou tentou-se enviar
		log.log("Enviar: arquivo "  + arq_lote + " completamente enviado")
		util.move(arq_lote, "LIXO")
		enviadas.remover(lote)
		return

	# O gateway chama de volta nosso método "registrar()" conforme a necessidade
	modulo_gateway.remeter(lote, conteudo)
