# -*- coding: utf-8

import datetime, os, time, glob
from src import log, recepcao, util, const

def registrar(lote, ID, provedor):
	# Registra mensagem enviada com sucesso ao provedor
	# para obter uma posterior confirmação positiva
	# Usa um arquivo por dia 
	arquivo = datetime.date.today().isoformat() + ".conf"
	arquivo = os.path.join("CONFIRMAR", arquivo)
	util.gravaseguro(arquivo, "%s,%f,%s\n" % (ID, time.time(), provedor))


def recibo(f):
	return f[:-5] + ".recibo"


def registrar_recibo(arquivo, ID, status, provedor):
	# Registra a confirmação positiva
	# Os arquivos ".conf" e ".recibo" sempre têm o mesmo prefixo,
	# de modo que os dois arquivos podem ser removidos quando todos
	# os IDs no primeiro constarem do segundo

	daemon = False

	if not arquivo:
		# Um arquivo neste formato nunca vai ser criado por registrar(),
		# então apenas a versão ".recibo" do mesmo vai existir, para
		# posterior checagem
		daemon = True
		arquivo = os.path.join("CONFIRMAR",
			time.strftime("%Y%m%d%H%M%S", time.gmtime(time.time())) + "-d.conf")

	arquivo = recibo(arquivo) # Troca '.conf' por '.recibo'
	util.gravaseguro(arquivo, "%s,%f,%d,%s\n" % (ID, time.time(), status, provedor))

	# Mandar também para OUTBOX, se não veio via HTTP
	# (Se veio via HTTP, o próximo processamento vai tratar o recibo)
	if not daemon:
		recepcao.registrar_recibo(ID, status)


def ler_arquivo(f):
	# Obtém lista de IDs a confirmar
	# Nós confiamos no formato deste arquivo pois é nosso próprio programa
	# que gera o mesmo
	dic = {}
	log.log("Confirmação: abrindo arquivo %s" % f)
	alista = open(f).readlines()
	alista = [ registro.strip().split(",") for registro in alista ]

	for registro in alista:
		if len(registro) < 3:
			log.admin("Registro corrompido em %s: %s" % (f, str(registro)))
			continue
		reg = {}
		reg["hora"] = registro[1]
		try:
			reg["hora"] = float(reg["hora"])
		except ValueError:
			log.admin("Registro corrompido em %s: %s" % (f, str(registro)))
			continue
		reg["provedor"] = registro[2]
		dic[registro[0]] = reg
	
	return dic
	

def ler_arquivo_conf(f):
	return ler_arquivo_conf_2(recibo(f))

def ler_arquivo_conf_2(f):
	# Obtém lista de IDs já confirmados
	# Nós confiamos no formato deste arquivo pois é nosso próprio programa
	# que gera o mesmo
	dic = {}

	if not os.path.exists(f):
		log.log("Confirmação: arquivo %s ainda não existe" % f)
		return dic

	log.log("Confirmação: abrindo arquivo %s" % f)
	alista = open(f).readlines()
	alista = [ registro.strip().split(",") for registro in alista ]

	for registro in alista:
		if len(registro) < 4:
			log.admin("Registro corrompido em %s: %s" % (f, str(registro)))
			continue
		reg = {}
		reg["hora"] = registro[1]
		reg["status"] = int(registro[2])
		reg["provedor"] = registro[3]
		dic[registro[0]] = reg
	
	return dic
	

def processar(modulo_gateway):
	# Percorre os arquivos de confirmação, consultando o provedor 
	# a respeito das mensagens a confirmar
	# Grava as confirmações na pasta RECEPCAO.
	# Remove os arquivos de confirmação totalmente satisfeitos

	# Obtém as mensagens confirmadas de forma assíncrona, distribuindo
	# as confirmações para os respectivos lotes e apagando os arquivos
	# originais

	# TODO isto significa que a confirmação só vai para OUTBOX quando
	# o processamento por lote é executado, quando poderia ser imediato.

	arqs = glob.glob(os.path.join("CONFIRMAR", "*-d.recibo"))
	# Evita race condition com servidor HTTP
	time.sleep(2)
	for r in arqs:
		msgs_confirmadas = ler_arquivo_conf_2(r)
		util.move(r, "LIXO")
		
		for f in glob.glob(os.path.join("CONFIRMAR", "*.conf")):
			msgs = ler_arquivo(f)
			for ID in msgs_confirmadas:
				 if ID in msgs:
					# Recibo pertence ao lote f
					log.log("Copiando recibo de %s vindo pelo HTTP" % ID)
					registrar_recibo(f, ID, msgs_confirmadas[ID]["status"],
						msgs_confirmadas[ID]["provedor"])
					if msgs[ID]["provedor"] != msgs_confirmadas[ID]["provedor"]:
						log.log("    Aviso: provedor diferente para mesmo ID")

	for f in glob.glob(os.path.join("CONFIRMAR", "*.conf")):
		msgs = ler_arquivo(f)
		msgs_confirmadas = ler_arquivo_conf(f)

		# Descarta mensagens já confirmadas
		for ID in msgs_confirmadas.keys():
			if ID in msgs:
				del msgs[ID]

		# 'Confirma' com timeout as mensagens muito antigas
		for ID in msgs:
			emissao = msgs[ID]["hora"]
			timeout = emissao + modulo_gateway.timeout(msgs[ID]["provedor"])
			if timeout < time.time():
				log.log("Mensagem %s com timeout" % ID)
				registrar_recibo(f, ID, const.CONFIRM_TIMEOUT,
						msgs[ID]["provedor"])
				

		if len(msgs.keys()) <= 0:
			# Todas as mensagens do arquivo já foram confirmadas
			# Tanto os arquivos .conf como .recibo podem ir ao lixo
			log.log("Todas as mensagens em %s foram confirmadas" % f)
			util.move(f, "LIXO")
			util.move(recibo(f), "LIXO")
			continue
			
		modulo_gateway.confirmar(msgs, f)
