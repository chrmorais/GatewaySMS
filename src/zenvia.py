# -*- coding: utf-8

import random
import datetime
import time

from src import log, const, defs

from humansms.service.MultipleMessageService import MultipleMessageService
from humansms.service.QueryService import QueryService
from humansms.bean.MultipleMessage import MultipleMessage

gateway = None

def timeout():
	''' retorna timeout em dias para a mensagem ser considerada perdida '''
	return 8

def set_gateway(g):
	global gateway
	gateway = g

def safe_int(codigo):
	try:
		n = int(codigo)
	except ValueError:
		log.log("Zenvia: código %s deveria ser um inteiro" % codigo)
		n = -1
	return n

tabela_status = {
	0: const.STATUS_ENVIADO,
	10: const.STATUS_MSGNULA,
	11: const.STATUS_MSGINVAL,
	12: const.STATUS_MSGGRANDE,
	13: const.STATUS_FONEINVAL,
	14: const.STATUS_FONENULO,
	15: const.STATUS_DATAINVAL,
	16: const.STATUS_IDINVAL,
	80: const.STATUS_IDENVIADO,
	141: const.STATUS_INTERNACIONAL
}

def traduzir_status_envio(codigo):
	if codigo not in tabela_status:
		log.log("Zenvia: código de erro de envio %d desconhecido" % codigo)
		return const.STATUS_OUTRO
	return tabela_status[codigo]

tabela_confirm = {
	120: const.CONFIRM_ENTREGUE,
	111: const.CONFIRM_SEMINFORMACAO,
	140: const.CONFIRM_NAOCOBERTO,
	145: const.CONFIRM_INATIVO,
	150: const.CONFIRM_EXPIRADA,
	160: const.CONFIRM_ERROREDE,
	161: const.CONFIRM_REJEITADA,
	162: const.CONFIRM_CANCELADA,
	170: const.CONFIRM_MSGINVAL,
	171: const.CONFIRM_NUMEROINVAL,
	130: const.CONFIRM_BLOQUEADA,
	131: const.CONFIRM_SPAM,
	141: const.CONFIRM_INTERNACIONAL,
	180: const.CONFIRM_IDDESCONHECIDO
}

def traduzir_status_confirm(codigo):
	if codigo not in tabela_confirm:
		log.log("Zenvia: código de confirmação %d desconhecido" % codigo)
		return const.CONFIRM_OUTRO
	return tabela_confirm[codigo]


date_format = "%d/%m/%Y %H:%M:%S"

def para_formato_data(timestamp):
	return time.strftime(date_format, time.localtime(timestamp))

def ler_formato_data(s):
	try:
		return time.mktime(time.strptime(s.strip(), date_format))
	except ValueError:
		log.log("Zenvia mandou data inválida %s" % s)
		return 0


def enviar(lote, msgs):
	send = MultipleMessageService(defs.get("zenvia_user"),
				defs.get("zenvia_password"))
	msg_d = []
	msg_e = []

	# O layout de remessa é diferente para mensagem com ou sem
	# agendamento, então é preciso separar antes
	for ID in msgs.keys():
		if msgs[ID]["hora"] <= 0:
			msg_d.append(ID)
		else:
			msg_e.append(ID)

	# Manda as mensagens em blocos de 100 para balancear entre
	# segurança de envio (ideal: mandar 1 em 1) e "custo" de cada
	# transação (demora do HTTP, tráfego de rede - ideal mandar tudo
	# de uma vez). O Zenvia limita a mensagem a 1MB e 5000 mensagens,
	# mas devemos estar bem abaixo deste limite.

	cb = 0
	if defs.get("zenvia_confirm_http"):
		# Confirmações deveriam ser obtidas exclusivamente via HTTP
		cb = 2

	for i in range(0, len(msg_d), 100):
		csv = ""
		bloco = msg_d[i : i + 100]
		for ID in bloco:
			csv += "%s;%s;%s;%s\n" % \
				(msgs[ID]["fone"], msgs[ID]["msg"], ID, defs.get("origem")[:20])

		try:
			res = send.sendMultipleListMsg(csv, MultipleMessage.TYPE_D, cb)
		except Exception as e:
			log.admin("Zenvia: envio: exceção %s" % str(e))
			break

		if not tratar_envio(bloco, res, lote):
			break

	for i in range(0, len(msg_e), 100):
		csv = ""
		bloco = msg_e[i : i + 100]
		for ID in bloco:
			csv += "%s;%s;%s;%s;%s\n" % \
				(msgs[ID]["fone"], msgs[ID]["msg"], ID, defs.get("origem")[:20],
				para_formato_data(msgs[ID]["hora"]))
			log.log("Mensagem %s agendada para %s" % \
				(ID, para_formato_data(msgs[ID]["hora"])))

		try:
			res = send.sendMultipleListMsg(csv, MultipleMessage.TYPE_E, cb)
		except Exception as e:
			log.admin("Zenvia: envio: exceção %s" % str(e))
			break

		if not tratar_envio(bloco, res, lote):
			break


def tratar_envio(bloco, resposta, lote):
	if not resposta:
		log.log("Zenvia: envio: resposta nula")
		return False

	estado = safe_int(resposta[0].getCode())

	if estado == 200:
		pass
	elif estado == 201:
		log.admin("Zenvia: envio: créditos foram todos gastos")
	elif estado == 240:
		log.admin("Zenvia: envio: arquivo vazio")
		return False
	elif estado == 241:
		log.admin("Zenvia: envio: arquivo grande demais")
		return False
	elif estado == 242:
		log.admin("Zenvia: envio: erro no arquivo enviado")
		return False
	elif estado == 900:
		log.admin("Zenvia: envio: erro de autenticação")
		return False
	elif estado == 990:
		log.admin("Zenvia: envio: limite da conta atingido")
		return False
	else:
		log.admin("Zenvia: envio: erro desconhecido %d" % estado)
		return False

	i = -1
	for omsg in resposta[1:]:
		i = i + 1
		# Código de erro do Zenvia
		estado_msg = safe_int(omsg.getCode())
		ID = bloco[i]

		if estado_msg >= 240:
			# Erros iguais ao estado geral tratado mais acima, a mensagem
			# não foi mandada mas continua na fila para ser mandada quando
			# o problema geral for resolvido
			continue

		# Código de erro do nosso sistema (const.py)
		estado_local = traduzir_status_envio(estado_msg)

		gateway.remeter_cb(lote, "Zenvia", {ID: {"status": estado_local}})
		log.log("Zenvia: envio: msg %s enviada, status envio %d %d" % \
				(ID, estado_msg, estado_local))

	return True


def confirmar(arquivo, msgs):
	if defs.get("zenvia_confirm_http"):
		# Confirmações deveriam ser obtidas exclusivamente via HTTP,
		# mas as vezes nao vem e tem de ser solicitadas positivamente

		ha_8_horas = time.time() - 8 * 60 * 60
		atrasadas = {}

		for ID in msgs.keys():
			msg = msgs[ID]
			if msg['hora'] < ha_8_horas:
				# consulta uma parte aleatoria das mensagens atrasadas
				# calcula segundos de atraso acima de 8h
				# FIXME: se resposta for 110, não consultar de novo!
				atraso = (0.0 + ha_8_horas - msg['hora']) / 3600.0
				# normaliza atraso: 8h = 0, 16h = 1.0, 24h = 2.0
				atraso_n = atraso / 8.0
				if atraso_n > 2.0:
					atraso_n = 2.0
				# atraso tendendo a 16, chance de ser consultado -> 11% por rodada
				# (baseado numa rodada a cada 15 minutos)
				chance = atraso_n * 0.11
				if random.random() < chance:
					log.log("Zenvia: confirm http msg %s atrasada; solicitando agora (chance %f)" % (ID, chance))
					atrasadas[ID] = msg

		log.log("Zenvia: %d mensagens atrasadas a consultar" % len(atrasadas))

		msgs = atrasadas

	err = False
	send = QueryService(defs.get("zenvia_user"), defs.get("zenvia_password"))

	ids = msgs.keys()
	for i in range(0, len(ids), 100):
		if err:
			break

		bloco = ids[i : i+100]
		try:
			res = send.queryMultipleStatus(bloco)
		except Exception as e:
			log.admin("Zenvia: confirmar: exceção %s" % str(e))
			break

		i = -1
		for o in res:
			i = i + 1
			ID = bloco[i]
			if not tratar_confirmacao(ID, o.getCode(), err, arquivo):
				err = True


def confirmar_http(dados):
	log.log("Zenvia: confcb: recebendo dados via HTTP")
	if "id" not in dados:
		log.log("Zenvia: confcb: id não recebido")
		return
	elif "status" not in dados:
		log.log("Zenvia: confcb: status não recebido")
		return
	elif not dados["id"]:
		log.log("Zenvia: confcb: Id nulo")
		return
	log.log("Zenvia: confcb: msg %s status %s" % (dados["id"], dados["status"]))
	tratar_confirmacao(dados["id"], dados["status"], False, None)


def tratar_confirmacao(ID, estado_str, err, arquivo):
	estado = safe_int(estado_str)

	if estado == 100 or estado == 110:
		log.log("Zenvia: confirmar: msg %s pendente com estado %d" \
				% (ID, estado))
		return True

	elif estado >= 900:
		if not err:
			log.admin("Zenvia: confirmar: msg %s erro %d" % \
				 (ID, estado))
		return False

	estado_local = traduzir_status_confirm(estado)

	if estado_local < 0:
		if not err:
			log.admin("Zenvia: confirmar: msg %s erro desconhecido %d %d" % \
				(ID, estado, estado_local))
		return False
		
	
	gateway.confirmar_cb("Zenvia", {ID: {"status": estado_local}}, arquivo)
	log.log("Zenvia: confirmar: msg %s confirmada com codigo %d %d" % \
			(ID, estado, estado_local))

	return True


def receber():
	# Zenvia não implementa mais recepção síncrona. Veja receber_http().
	pass


def receber_http(dados):
	log.log("Zenvia: recebcb: recebendo dados via HTTP")
	if "id" not in dados:
		log.log("Zenvia: recebcb: falta ID")
		return
	elif "from" not in dados:
		log.log("Zenvia: recebcb: falta from")
		return
	elif "msg" not in dados:
		log.log("Zenvia: recebcb: falta msg")
		return
	elif "date" not in dados:
		log.log("Zenvia: recebcb: falta date")
		return
	elif not dados["id"]:
		log.log("Zenvia: recebcb: ID nulo")
		return

	ID = dados["id"]
	if "idMT" in dados:
		if dados["idMT"]:
			# Mensagem de resposta; id é o da pergunta
			ID = dados["idMT"]

	# Zenvia converte mensagens acentuadas para ASCII puro

	lista = [ {
			"ID": ID,
			"hora": ler_formato_data(dados["date"]),
			"fone": dados["from"],
			"msg": dados["msg"]
		} ]

	log.log("Zenvia: recebcb: msg %s origId %s fone %s msg %s" % \
		(ID, dados["id"], dados["from"], dados["msg"]))

	gateway.receber_cb("Zenvia", lista)
