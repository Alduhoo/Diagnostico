from google.appengine.ext import db

# Definicion de los temas a los cuales pertenecen las preguntas
class Tema(db.Model):
	nombre = db.StringProperty()
	descripcion = db.TextProperty()

class Pregunta(db.Model):
	pregunta = db.StringProperty()
	tema = db.ReferenceProperty(Tema)
	respuesta1 = db.StringProperty()
	respuesta2 = db.StringProperty()
	respuesta3 = db.StringProperty()
	respuesta4 = db.StringProperty()
	correcta = db.IntegerProperty()

	def texto_correcta(self):
		return self.respuesta1 if self.correcta == 1 else\
			   self.respuesta2 if self.correcta == 2 else\
			   self.respuesta3 if self.correcta == 3 else\
	           self.respuesta4 if self.correcta == 4 else\
	           ''
	def texto_opcion(self, x):
		return self.respuesta1 if x == 1 else\
			   self.respuesta2 if x == 2 else\
			   self.respuesta3 if x == 3 else\
	           self.respuesta4 if x == 4 else\
	           ''

class Examen(db.Model):
	calificacion = db.IntegerProperty()
	usuario = db.StringProperty()
	fecha = db.DateTimeProperty()

	def reporte(self):
		reporte = Reporte.gql("WHERE minimo <= :1 ORDER BY minimo DESC LIMIT 1", self.calificacion).get()
		return reporte

	def respuestas(self):
		respuestas = RespuestaExamen.gql("WHERE examen = :1", self.key())
		return respuestas

class Reporte(db.Model):
	nombre = db.StringProperty()
	descripcion = db.TextProperty()
	minimo = db.IntegerProperty()

class RespuestaExamen(db.Model):
	examen = db.ReferenceProperty(Examen)
	pregunta = db.ReferenceProperty(Pregunta)
	respuesta = db.IntegerProperty()

	def es_correcta(self):
		return self.respuesta == self.pregunta.correcta