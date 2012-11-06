import jinja2
import os
import cgi
import urllib
import datetime
import random

import webapp2
import webapp2_extras.appengine.users
import models

from google.appengine.api import users

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Logout(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			self.redirect(users.create_logout_url('/'), abort=True)
		else:
			self.redirect('/')

class Login(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url('/'), abort=True)
		else:
			self.redirect('/')

class MainHandler(webapp2.RequestHandler):
    def get(self):
        #generacion del template usando jinja
        template = jinja_environment.get_template('includes/index.html')
        #valores = {'productos' : productos, 'error' : error}
        #self.response.out.write(template.render(valores))
        self.response.out.write(template.render())

class Temas(webapp2.RequestHandler):
	@webapp2_extras.appengine.users.admin_required
	def get(self):
		# generar template
		template = jinja_environment.get_template('includes/temas.html')
		# obtener modelo
		temas = models.Tema.all()
		# Poner modelo en template y generar template
		valores = { 'temas' : temas }
		self.response.out.write(template.render(valores))

# class NuevoTema(webapp2.RequestHandler):
# 	def get(self):
# 		# generar template
# 		template = jinja_environment.get_template('includes/editarTema.html')
# 		# Generar template
# 		self.response.out.write(template.render())

class ActualizarTema(webapp2.RequestHandler):
	def post(self):
		#obtener datos de la forma
		nombre = cgi.escape(self.request.get('nombre'))
		descripcion = cgi.escape(self.request.get('descripcion'))
		key = cgi.escape(self.request.get('key'))
		error = False

		#validar restricciones
		if len(nombre) <= 0:
			error = True
		if len(descripcion) <= 0:
			error = True

		# TODO: redirigir si hay mala forma
		# if error:
		# 	self.redirect('/Productos?error=True', abort=True)

		#obtener objeto
		if (key):
			tema = models.Tema.get(key)
		else:
			tema = models.Tema()
		tema.nombre = nombre
		tema.descripcion = descripcion

		#guardar en bd
		tema.put()
		self.redirect('/temas')

class FormaTema(webapp2.RequestHandler):
	@webapp2_extras.appengine.users.admin_required
	def get(self):
		# obtener datos del query string
		key = cgi.escape(self.request.get('key'))
		# generar template
		template = jinja_environment.get_template('includes/editarTema.html')
		# obtener modelo
		if (key):
			tema = models.Tema.get(key)
		else:
			tema = None
		# Poner modelo en template y generar template
		valores = { 'tema' : tema }
		self.response.out.write(template.render(valores))

class Preguntas(webapp2.RequestHandler):
	@webapp2_extras.appengine.users.admin_required
	def get(self):
		# generar template
		template = jinja_environment.get_template('includes/preguntas.html')
		# obtener modelo
		preguntas = models.Pregunta.all()
		# Poner modelo en template y generar template
		valores = { 'preguntas' : preguntas }
		self.response.out.write(template.render(valores))

class FormaPregunta(webapp2.RequestHandler):
	@webapp2_extras.appengine.users.admin_required
	def get(self):
		# obtener datos del query string
		key = cgi.escape(self.request.get('key'))
		# generar template
		template = jinja_environment.get_template('includes/editarPregunta.html')
		# obtener modelo
		if (key):
			pregunta = models.Pregunta.get(key)
		else:
			pregunta = None
		temas = models.Tema.all()
		# Poner modelo en template y generar template
		valores = { 'pregunta' : pregunta, 'temas' : temas }
		self.response.out.write(template.render(valores))

class ActualizarPregunta(webapp2.RequestHandler):
	def post(self):
		#obtener datos de la forma
		pregunta = cgi.escape(self.request.get('pregunta'))
		temaKey = cgi.escape(self.request.get('temaKey'))
		respuesta1 = cgi.escape(self.request.get('respuesta1'))
		respuesta2 = cgi.escape(self.request.get('respuesta2'))
		respuesta3 = cgi.escape(self.request.get('respuesta3'))
		respuesta4 = cgi.escape(self.request.get('respuesta4'))
		correcta = cgi.escape(self.request.get('correcta'))
		key = cgi.escape(self.request.get('key'))
		error = False

		#validar restricciones
		if len(pregunta) <= 0:
			error = True
		if len(temaKey) <= 0:
			error = True

		# TODO: redirigir si hay mala forma
		# if error:
		# 	self.redirect('/Productos?error=True', abort=True)

		#obtener objeto
		if (key):
			preg = models.Pregunta.get(key)
		else:
			preg = models.Pregunta()
		preg.pregunta = pregunta
		preg.tema = models.Tema.get(temaKey)
		preg.respuesta1 = respuesta1
		preg.respuesta2 = respuesta2
		preg.respuesta3 = respuesta3
		preg.respuesta4 = respuesta4
		preg.correcta = int(correcta)

		#guardar en bd
		preg.put()
		self.redirect('/preguntas')

class Examen(webapp2.RequestHandler):
	@webapp2_extras.appengine.users.login_required
	def get(self):
		# user = users.get_current_user()
		# if not user:
		# 	self.redirect(users.create_login_url('examen'), abort=True)
		# generar template
		template = jinja_environment.get_template('includes/examen.html')
		# obtener preguntas
		preguntas_keys = models.Pregunta.all(keys_only = True)
		total = preguntas_keys.count()
		total = min(total, 10)
		llaves = []
		for key in preguntas_keys:
			llaves.append(key)
		# preguntas = models.Pregunta.get(preguntas_keys)
		preguntas = models.Pregunta.get(random.sample(llaves, total))

		# Poner modelo en template y generar template
		valores = { 'preguntas' : preguntas }
		self.response.out.write(template.render(valores))
	# Calificar examen
	def post(self):
		user = users.get_current_user()
		correctas = 0
		contestadas = 0

		for argument in self.request.arguments():
			pregunta = models.Pregunta.get(argument)
			opcion = int(self.request.get(argument))
			if opcion == pregunta.correcta:
				correctas += 1
			contestadas += 1

		calif = int(1.0 * correctas / contestadas * 100)
		examen = models.Examen()
		examen.calificacion = calif
		examen.usuario = user.email()
		examen.fecha = datetime.datetime.now()
		examen.put()
		# TODO: redirect despues de contestar examen

class Examenes(webapp2.RequestHandler):
	@webapp2_extras.appengine.users.admin_required
	def get(self):
		# generar template
		template = jinja_environment.get_template('includes/examenes.html')
		# obtener modelo
		examenes = models.Examen.all()
		# Poner modelo en template y generar template
		valores = { 'examenes' : examenes }
		self.response.out.write(template.render(valores))

class Reportes(webapp2.RequestHandler):
	@webapp2_extras.appengine.users.admin_required
	def get(self):
		# generar template
		template = jinja_environment.get_template('includes/reportes.html')
		# obtener modelo
		reportes = models.Reporte.all()
		# Poner modelo en template y generar template
		valores = { 'reportes' : reportes }
		self.response.out.write(template.render(valores))

class Reporte(webapp2.RequestHandler):
	@webapp2_extras.appengine.users.login_required
	def get(self):
		key = cgi.escape(self.request.get('key'))
		# generar template
		template = jinja_environment.get_template('includes/reporte.html')
		# obtener modelo
		reporte = models.Reporte.get(key)
		# Poner modelo en template y generar template
		valores = { 'reporte' : reporte }
		self.response.out.write(template.render(valores))

class FormaReporte(webapp2.RequestHandler):
	@webapp2_extras.appengine.users.admin_required
	def get(self):
		# obtener datos del query string
		key = cgi.escape(self.request.get('key'))
		# generar template
		template = jinja_environment.get_template('includes/editarReporte.html')
		# obtener modelo
		if (key):
			reporte = models.Reporte.get(key)
		else:
			reporte = None
		# Poner modelo en template y generar template
		valores = { 'reporte' : reporte }
		self.response.out.write(template.render(valores))

class ActualizarReporte(webapp2.RequestHandler):
	def post(self):
		#obtener datos de la forma
		nombre = cgi.escape(self.request.get('nombre'))
		descripcion = cgi.escape(self.request.get('descripcion'))
		minimo = cgi.escape(self.request.get('minimo'))
		key = cgi.escape(self.request.get('key'))
		error = False

		#validar restricciones
		if len(nombre) <= 0:
			error = True
		if len(descripcion) <= 0:
			error = True
		if len(minimo) <= 0:
			error = True

		# TODO: redirigir si hay mala forma
		# if error:
		# 	self.redirect('/Productos?error=True', abort=True)

		#obtener objeto
		if (key):
			reporte = models.Reporte.get(key)
		else:
			reporte = models.Reporte()
		reporte.nombre = nombre
		reporte.descripcion = descripcion
		reporte.minimo = int(minimo)

		#guardar en bd
		reporte.put()
		self.redirect('/reportes')

class Resultados(webapp2.RequestHandler):
	@webapp2_extras.appengine.users.login_required
	def get(self):
		user = users.get_current_user()
		# generar template
		template = jinja_environment.get_template('includes/examenes.html')
		# obtener modelo
		examenes = models.Examen.gql("WHERE usuario = :email", email=user.email())
		# Poner modelo en template y generar template
		valores = { 'examenes' : examenes }
		self.response.out.write(template.render(valores))


app = webapp2.WSGIApplication([('/', MainHandler),
							   ('/logout', Logout),
							   ('/login', Login),
							   ('/temas', Temas),
							   ('/temas/nuevo', FormaTema),
							   ('/temas/actualizar', ActualizarTema),
							   ('/temas/editar', FormaTema),
							   ('/preguntas', Preguntas),
							   ('/preguntas/nuevo', FormaPregunta),
							   ('/preguntas/actualizar', ActualizarPregunta),
							   ('/preguntas/editar', FormaPregunta),
							   ('/examen', Examen),
							   ('/examenes', Examenes),
							   ('/reporte', Reporte),
							   ('/reportes', Reportes),
							   ('/reportes/nuevo', FormaReporte),
							   ('/reportes/editar', FormaReporte),
							   ('/reportes/actualizar', ActualizarReporte),
							   ('/resultados', Resultados)],
                              debug=True)
