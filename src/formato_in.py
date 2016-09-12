# -*- coding: utf-8

# Interpreta o formato CSV de mensagens SMS a serem remetidas
# Formato: vírgula separa campos, campos alfanuméricos são cercados
# por aspas. Cada registro é terminado por newline.
# Campos alfanuméricos não fechados podem ter newline no meio da
# mensagem. Campos com aspas no conteúdo devem escapear as aspas com \.
#
# Campos: ID, charset, telefone, hora para envio (ou 0), mensagem.
# Hora para envio é numérica, os demais campos são alfanuméricos.
# ID deve ser único "para sempre" e pode ser tanto um número sequencial
# quanto um hash.
#
# Hora: número de segundos desde 01/01/1970. Se igual a zero, a
# mensagem pode ser enviada imediatamente.

import time

def acentuado(s):
	# Verifica se há algum caractere especial (acentuado)
	for i in range(0, len(s)):
		if ord(s[i]) >= 128:
			return True
	return False

def converter_utf8(s, charset):
	# Converte qualquer mensagem acentuada para UTF-8
	# Todo o tráfego interno de mensagem é em UTF-8, se o provedor
	# SMS pede outro formato (como UCS-2) o "driver" é responsável
	# pela recodificação.
	try:
		u = s.decode(charset)
	except UnicodeError:
		return None
	return u.encode('utf-8')

def parse_inicial(s):
	err = None
	lista = []
	registro = []
	campo = None
	habilitado = True
	linha = 1
	slinha = ""

	i = -1

	while i < (len(s) - 1):
		i += 1
		c = s[i]
		slinha += c

		if c == "\r" or c == "\n":
			if campo is not None:
				# Adiciona último campo antes do fim da linha
				registro.append(campo)
			if registro:
				# Só adiciona linhas não-vazias
				lista.append(registro)
			registro = []
			campo = None
			linha += 1
			slinha = ""
		elif c == ";":
			# Se há separador há pelo menos dois campos
			if campo is None:
				campo = ""
			registro.append(campo)
			campo = ""
		else:
			if campo is None:
				campo = ""
			campo += c

	return lista, err

def parse(s):
	dlista = []

	lista, err = parse_inicial(s)
	if err:
		return None, err

	err = None

	for i in range(0, len(lista)):
		registro = lista[i]
		if len(registro) <> 5:
			err = "Linha %d não tem o número esperado de campos" % (i + 1)
			break

		ID, charset, telefone, shora, msg = registro

		ID = ID.strip()
		charset = charset.strip()
		shora = shora.strip()
		telefone = telefone.strip()
		msg = msg.strip()

		try:
			tmp = "" + ID + charset + telefone + msg + shora
		except TypeError:
			err = "Linha %d, campo não alfanumérico" % (i + 1)
			break

		if not ID:
			err = "Linha %d, ID nulo" % (i + 1)
			break

		if not charset:
			err = "Linha %d, charset nulo" % (i + 1)
			break

		# telefone nulo são reportados como erros a posteriori

		if acentuado(msg):
			msg_utf8 = converter_utf8(msg, charset)
			if msg_utf8 is None:
				err = "Linha %d, mensgem inválida para o charset" % (i + 1)
				break
			msg = msg_utf8

		if not shora:
			hora = 0
		else:
			formato = "%d/%m/%Y %H:%M:%S"
			try:
				hora = time.mktime(time.strptime(shora.strip(), formato))
			except ValueError:
				err = "Linha %d, data inválida %s" % (i + 1, shora)
				break

		if hora < time.time():
			# print "agendamento retroativo em %dh" % ((hora - time.time()) / 3600)
			hora = 0

		dlista.append({"id": ID, "msg": msg, "fone": telefone, "hora": hora})

	return dlista, err
