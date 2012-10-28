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

class Examen(db.Model):
	calificacion = db.IntegerProperty()
	usuario = db.StringProperty()
	fecha = db.DateTimeProperty()

	def reporte(self):
		reporte = Reporte.gql("WHERE minimo <= :1 ORDER BY minimo DESC LIMIT 1", self.calificacion).get()
		return reporte

class Reporte(db.Model):
	nombre = db.StringProperty()
	descripcion = db.TextProperty()
	minimo = db.IntegerProperty()