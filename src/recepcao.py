# -*- coding: utf-8

import os, time, glob
from src import log, util, defs

date_format = "%d/%m/%Y %H:%M:%S"

def registrar_recibo(ID, status):
	# Registra mensagem enviada e confirmada, ou com
	# erro fatal que impede seu envio.
	# Esta função é normalmente chamada pelo módulo de confirmação,
	# mas também por pelo módulo "enviar" para mensagens que falham.

	if defs.get("daemon"):
		# Nome diferente para o serviço HTTP não tropeçar no processamento de lote
		# No momento esta opção não é usada porque todos os recibos vindos via
		# HTTP são efetivamente aceitos apenas no processamento do lote
		arquivo = time.strftime("%Y%m%d%H%M%S", time.gmtime(time.time())) + "-d.env"
	else:
		arquivo = defs.get("timestamp") + ".env"

	arquivo = os.path.join("RECEPCAO", arquivo)

	# Grava no formato CSV com vistas a ir para OUTBOX
	util.gravaseguro(arquivo,
		"Confirmacao;%s;%s;%d\r\n" %
		(ID, time.strftime(date_format,
				time.localtime(time.time())),
		status))


def registrar_recebida(ID, g, fone, hora, msg):
	# Registra mensagem recebida (mandada pelo usuário).
	# ID só é existe/é válido se a mensagem foi mandada
	# em resposta a um SMS anterior enviado por nós.

	if defs.get("daemon"):
		# Nome diferente para o serviço HTTP não tropeçar no processamento de lote
		arquivo = time.strftime("%Y%m%d%H%M%S", time.gmtime(time.time())) + "-d.rec"
	else:
		arquivo = defs.get("timestamp") + ".rec"

	arquivo = os.path.join("RECEPCAO", arquivo)

	# Escapa aspas
	# msg = msg.replace("\"", "\"\"")

	# Grava no formato CSV com vistas a ir para OUTBOX
	util.gravaseguro(arquivo,
		"Recebida;%s;%s;%s;%s;%s\r\n" %
		(ID, g, time.strftime(date_format,
				time.localtime(hora)),
		fone, msg))


def processar(modulo_gateway):
	# Recebe eventuais SMS dos divesos gateways SMS
	modulo_gateway.receber()
	# copiar para OUTBOX
	copiar()

def copiar():
	# Transfere todos os arquivos de recepcao para OUTBOX.
	# A função util.move() garante que o arquivo é copiado
	# com outro nome se existe um homônimo em OUTBOX.

	# Se daemon, tenta obter a trava para não concorrer com o serviço de lote
	if defs.get("daemon"):
		if not trava.obter():
			# Fica para a próxima tentativa
			return

	arqs = glob.glob(os.path.join("RECEPCAO", "*"))
	# Dorme 2 segundos para evitar race condition com serviço HTTP
	time.sleep(2)
	for f in arqs:
		util.move(f, "OUTBOX")
	time.sleep(1)

	if defs.get("daemon"):
		trava.soltar()
