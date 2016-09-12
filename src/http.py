# -*- coding: utf-8

import BaseHTTPServer
import SocketServer
import cgi
import urlparse
from . import zenvia, log

PORT = 33774

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
	def setup(self):
		self.timeout = 10
		BaseHTTPServer.BaseHTTPRequestHandler.setup(self)
		# self.request.settimeout(5)

	def do_GET(self):
		log.log("HTTP GET")
		parsed_path = urlparse.urlparse(self.path)
		raw_form = urlparse.parse_qs(parsed_path.query)

		form = {}
		for f in raw_form.keys():
			form[f] = raw_form[f][0]

		self.despachar(parsed_path.path, form)

	def do_POST(self):
		log.log("HTTP POST")
		parsed_path = urlparse.urlparse(self.path)
		# Parse the form data posted
		raw_form = cgi.FieldStorage(
			fp=self.rfile, 
			headers=self.headers,
			environ={
				'REQUEST_METHOD':'POST',
				'CONTENT_TYPE': self.headers['Content-Type'],
			})

		form = {}
		for f in raw_form.keys():
			form[str(f)] = str(raw_form.getvalue(f))

		self.despachar(parsed_path.path, form)

	def despachar(self, uri, form):
		if uri == "/recebsms":
			# URL de call-back Zenvia
			self.receb_sms(form)
		elif uri == "/statussms":
			# URL de call-back Zenvia
			self.receb_status(form)
		elif uri == "/ping.html":
			self.pong()
		else:
        		self.send_response(404)
        		self.end_headers()
        		self.wfile.write("NOK")

	def pong(self):
		self.send_response(200)
		self.end_headers()
		self.wfile.write("**42**")

	def receb_sms(self, data):
		zenvia.receber_http(data)
        	self.send_response(200)
        	self.end_headers()
        	self.wfile.write("OK receb")

	def receb_status(self, data):
		zenvia.confirmar_http(data)
        	self.send_response(200)
        	self.end_headers()
        	self.wfile.write("OK status")


def servir():
	httpd = BaseHTTPServer.HTTPServer(("", PORT), Handler)
	httpd.serve_forever()
	# TODO cópia dos arquivos em RECEPCAO ainda é feita pelo
	# processamento de lote, o que pode demorar.
