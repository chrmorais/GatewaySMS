# -*- coding: utf-8

import random
import datetime
import time
from src import log, const, defs

# Gateway falso para fins de testes.

gateway = None

def timeout():
	''' retorna timeout em dias para a mensagem ser considerada perdida '''
	return 1

def set_gateway(g):
	global gateway
	gateway = g

def enviar(lote, msgs):
	for ID in msgs.keys():
		x = random.choice([0, 1, 2])
		if x == 0:
			# simular sucesso
			hora = msgs[ID]["hora"]
			if hora <= 0:
				hora = "agora"
			else:
				hora = datetime.datetime.fromtimestamp(hora).isoformat()
			log.log("(FAKE) mensagem %s enviada, agendada para %s" % (ID, hora))
			gateway.remeter_cb(lote, "Fake", {ID: {"status": const.STATUS_ENVIADO}})
		elif x == 1:
			# fracasso por motivo não inerente a mensagem;
			# não retornar status, tentará na próxima vez
			log.log("(FAKE) mensagem %s não enviada" % ID)
			pass
		elif x == 2:
			# simular fracasso por culpa da mensagem
			log.log("(FAKE) mensagem %s falhada" % ID)
			gateway.remeter_cb(lote, "Fake", {ID: {"status": const.STATUS_FONEINVAL}})


def confirmar(arquivo, msgs):
	for ID in msgs.keys():
		x = random.choice([0, 1, 2])
		if x == 0:
			# simular sucesso
			log.log("(FAKE) mensagem %s entregue" % ID)
			gateway.confirmar_cb("Fake", {ID: {"status": const.CONFIRM_ENTREGUE}}, arquivo)
		elif x == 1:
			# fracasso por motivo não inerente a mensagem;
			# não retornar status, tentará na próxima vez
			log.log("(FAKE) mensagem %s sem status definitivo" % ID)
			pass
		elif x == 2:
			# simular fracasso
			log.log("(FAKE) mensagem %s não entregue" % ID)
			gateway.confirmar_cb("Fake", {ID: {"status": const.CONFIRM_INATIVO}}, arquivo)


def receber():
	lista = []
	for i in range(0, random.randint(0, defs.get("fake_rec"))):
		msg = {"ID": random.choice(["14240", "3422", "1", "2", "3", "4", "5", "6"]),
			"fone": "554788883331",
			"hora": int(time.time() - random.randint(0, 3600)),
			"msg": random.choice(["abcde", "abcde\"\"fg", u"áéí\"óú".encode("utf-8")])}
		lista.append(msg)
	gateway.receber_cb("Fake", lista)
