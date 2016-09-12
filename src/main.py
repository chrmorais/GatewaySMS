#!/usr/bin/env python
# -*- coding: utf-8

import sys

from . import trava
from . import inbox
from . import gateway
from . import enviar
from . import confirmacao
from . import recepcao
from . import log
from . import defs

def main(defaults):
	defs.read(defaults)

	if not trava.obter():
		log.log("Outra cópia do programa ainda em execução")
		if trava.tempo() > 10800:
			log.admin("Gateway SMS pode estar travado, favor verificar")
			sys.exit(1)
		sys.exit(0)
	
	if not trava.limpo():
		log.admin("O Envia-SMS pode ter terminado com erro na última execução, favor verificar")

	trava.cronometrar()

	inbox.processar()
	enviar.processar(gateway)
	confirmacao.processar(gateway)
	recepcao.processar(gateway)
	
	trava.parar_cronometro()
	trava.soltar()
