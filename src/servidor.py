# -*- coding: utf-8

import sys

from . import http
from . import defs
from . import gateway # apenas para carregar os módulos de provedor

def main(defaults):
	defs.read(defaults)
	http.servir()
