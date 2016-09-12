# -*- coding: utf-8

import sys
from src import log, const, fakegate, zenvia, telefone, defs, enviar, recepcao, confirmacao

provedores = {"Fake": fakegate, "Zenvia": zenvia}
# provedores = {"Zenvia": zenvia}

for p in provedores:
	provedores[p].set_gateway(sys.modules[__name__])

def timeout(provedor):
	# Retorna timeout de uma mensagem enviada ao provedor, em segundos
	dias = 7

	if provedor in provedores:
		dias = provedores[provedor].timeout()
	else:
		log.log("Provedor %s desconhecido (timeout default)" % provedor)

	return dias * 24 * 3600

def remeter(lote, dic):
	# Efetivamente faz uso dos provedores disponíveis para remeter as mensagens

	# dicionário de mensagens separado por gateway/operadora
	gdic = {}
	for p in provedores.keys():
		gdic[p] = {}

	# separa as mensagens por gateway/operadora, que é escolhida
	# com base no número do telefone. O módulo 'telefone' também
	# verifica o número e adiciona país e DDD se o número não tem.
	#
	# Mensagens com número flagrantemente inválido são rejeitadas
	# já neste ponto, com status diferentes dos erros do gateway,
	# para diferenciar entre erro local e remoto.

	log.log("Mensagens a enviar, no total: %d" % len(dic.keys()))

	for ID in dic.keys():
		registro = dic[ID]
		fone, provedor, err = telefone.consistir(registro["fone"])
		if err:
			log.log("Mensagem %s rejeitada localmente, telefone inválido" % ID)
			enviar.registrar(lote, ID, const.STATUS_FONEINVAL_LOCAL, provedor)
			continue
		elif len(registro["msg"]) <= 0:
			log.log("Mensagem %s rejeitada localmente, msg nula" % ID)
			enviar.registrar(lote, ID, const.STATUS_MSGNULA_LOCAL, provedor)
			continue
		elif len(registro["msg"] + " " + defs.get("origem")) > 140:
			log.log("Mensagem %s rejeitada localmente, msg muito comprida" % ID)
			enviar.registrar(lote, ID, const.STATUS_MSGGRANDE_LOCAL, provedor)
			continue
			
		registro["fone"] = fone
		gdic[provedor][ID] = registro

	# Remete as mensagens pelos provedores

	for g in gdic.keys():
		provedor = provedores[g]
		msgs = gdic[g]

		# Alguns provedores suportam o envio de múltiplas mensagens
		# por transação, então a API aceita um dicionário direto
		if msgs.keys():
			log.log("Mensagens a enviar pelo provedor %s: %d" % (g, len(msgs.keys())))
			provedor.enviar(lote, msgs)


def remeter_cb(lote, provedor, lista):
	# Callback chamado pelo provedor. Será chamado várias vezes para cada
	# chamada de provedor.enviar() de modo a registrar os status em disco
	# o mais rápido possível (e.g. de 50 em 50 envios, em vez de esperar
	# milhares de mensagens serem mandadas)

	log.log("Relatórios de status recebidos: %d" % len(lista.keys()))
	for ID in lista.keys():
		enviar.registrar(lote, ID, lista[ID]["status"], provedor)



def confirmar(msgs, f):
	# Separa as mensagens a confirmar por provedor
	gmsgs = {}

	for g in provedores.keys():
		gmsgs[g] = {}

	for ID in msgs.keys():
		msg = msgs[ID]
		if msg["provedor"] not in gmsgs:
			log.log("Provedor %s desconhecido" % msg["provedor"])
			confirmacao.registrar_recibo(f, ID, msg["fone"], const.CONFIRM_GATEWAYINVAL, msg["provedor"])
			continue
		gmsgs[msg["provedor"]][ID] = msg

	# Solicita as confirmações para cada provedor

	for g in gmsgs.keys():
		provedor = provedores[g]
		msgs = gmsgs[g]

		if msgs.keys():
			log.log("Mensagens a confirmar pelo provedor %s: %d" % (g, len(msgs.keys())))
			provedor.confirmar(f, msgs)


def confirmar_cb(provedor, confirms, arquivo):
	# Callback chamado pelo provedor.
	log.log("Relatórios de confirmacao recebidos: %d" % len(confirms.keys()))
	for ID in confirms.keys():
		msg = confirms[ID]
		confirmacao.registrar_recibo(arquivo, ID, msg["status"], provedor)
	

def receber():
	# Requisitar mensagens recebidas dos diversos provedores

	for g in provedores.keys():
		provedores[g].receber()


def receber_cb(provedor, recebidas):
	# Chamada pelo módulo do provedor quando uma mensagem é recebida

	log.log("Mensagens recebidas de %s: %d" % (provedor, len(recebidas)))
	for msg in recebidas:
		recepcao.registrar_recebida(msg["ID"], provedor, msg["fone"], msg["hora"], msg["msg"])
