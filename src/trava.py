# -*- coding: utf-8

import time, socket, os
from src import log

sk = None

def obter():
	# Obtém um recurso que apenas um processo de cada vez pode ter
	global sk
	sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		sk.bind(("127.0.0.1", 56789))
	except (socket.error):
		return False;

	sk.listen(1)

	log.log("Trava obtida")
	return True

def soltar():
	global sk
	sk.close()
	log.log("Trava liberada")

def limpo():
	if tempo(True) <> -1:
		# Não deveria haver registro em tempo.txt neste ponto
		return False
	return True

def cronometrar():
	# Registra o início da atividade
	t = open(os.path.join("STAT", "tempo.txt"), "w")
	t.write("%f" % time.time())
	t.flush();
	os.fsync(t.fileno())
	t.close()
	log.log("Trava registrou a hora inicial de execução")

def parar_cronometro():
	os.unlink(os.path.join("STAT", "tempo.txt"))
	log.log("Trava: registrou final de execução")

def tempo(erro_esperado=False):
	# Retorna há quanto tempo, em segundos, o software já está rodando
	# (ou há quanto tempo está travado)
	#
	# A função "limpo" chama esta função com parâmetro True, pois
	# já espera que não haja nenhum registro.

	t = -1
	try:
		ts = open(os.path.join("STAT", "tempo.txt")).read()
		t = float(ts)
	except (IOError, OSError):
		if not erro_esperado:
			log.log("Não pode ler tempo.txt")
		return -1
	except ValueError:
		if not erro_esperado:
			log.log("Conteúdo de tempo.txt inválido")
		return -1
	return time.time() - t
