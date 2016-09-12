#!/usr/bin/env python
# -*- coding: utf-8

import sys, glob
from src import defs, formato_in, telefone

defaults = {}
defaults["email"] = "root@localhost"
defaults["ddi"] = "55"
defaults["ddd"] = "47"
defaults["teste"] = True
defaults["provedor"] = "Fake"

defs.read(defaults)

for f in glob.glob("tests/ruim*.csv"):
	csv = open(f).read()
	lista, err = formato_in.parse(csv)
	if not err:
		print "Aceitou arquivo inválido " + f
		print lista
		sys.exit(1)
	# print f, err

csv = open("tests/bom.csv").read()
lista, err = formato_in.parse(csv)
if err or len(lista) < 20:
	print "Erro de parsing do arquivo CSV bom"
	print err
	sys.exit(1)

print lista

csv = open("tests/bom2.csv").read()
lista, err = formato_in.parse(csv)
if err or len(lista) <> 9:
	print "Erro de parsing do arquivo CSV bom II"
	print err
	sys.exit(1)

print lista

fones = [
	["99887765", "554799887765", False],
	["988-7765", "", True],
	["5547888033316105", "", True],
	["9988-7765", "554799887765", False],
	[" 9988-7765 celular", "554799887765", False],
	["(47) 9988-7765", "554799887765", False],
	["(047) 9988-7765", "554799887765", False],
	["(47) 99887765", "554799887765", False],
	["+55 (47) 99887765", "554799887765", False],
	["0055 47 99887765", "554799887765", False],
	["4799887765", "554799887765", False],
	["04799887765", "554799887765", False]
	]

# Algoritmo de consistência não é robusto para números internacionais
# ["+1 233 555-1234", "12335551234", False],
# ["001 233 555-1234", "12335551234", False],

for t in fones:
	t1, gateway, err = telefone.consistir(t[0])
	if (t[2] and not err) or (not t[2] and err) or ((not t[2]) and (t1 <> t[1])):
		print "Telefone %s -> %s esperado %s; erro %s esperado %s" % \
			(t[0], t1, t[1], err, t[2])
		sys.exit(1)

print "###########"
print "Testes OK"
print "###########"
