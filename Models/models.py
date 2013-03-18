import re
import webapp2
from google.appengine.api import urlfetch
from BeautifulSoup import *
from google.appengine.ext import db
import json as simplejson
import os
from google.appengine.ext.webapp import template
from google.appengine.api import taskqueue
from parse_rest.connection import register
from settings_local import *
from parse_rest.datatypes import Object


def gql_json_parser(query_obj):
    result = []
    for entry in query_obj:
        result.append(dict([(p, (unicode(getattr(entry, p)))) for p in entry.properties()]))
    return result
    
class Fraccion(db.Model):
    nombre = db.StringProperty(required= False)
    def __unicode__(self):
        return self.nombre

        
class Comision(db.Model):
    nombre = db.StringProperty(required= False)
    num = db.StringProperty(required= False)
    def __unicode__(self):
        return self.nombre



class Entidad(db.Model):
    nombre = db.StringProperty(required= False)
    def __unicode__(self):
        return self.nombre

    
class Diputado(db.Model):
    nombre = db.StringProperty()
    distrito = db.IntegerProperty(default=0)
    nu_diputado = db.IntegerProperty(default=0)
    fraccion = db.ReferenceProperty(Fraccion,collection_name="fraccion")
    cabecera =  db.StringProperty()
    tipo_de_eleccion = db.StringProperty()
    entidad = db.ReferenceProperty(Entidad,collection_name="entidad")
    curul = db.StringProperty()
    suplente = db.StringProperty()
    email = db.EmailProperty()
    onomastico = db.StringProperty()
    foto = db.URLProperty()
    

        
    def __unicode__(self):
        return self.nombre

class Iniciativa(db.Model):
    nombre = db.StringProperty(required= False)
    num = db.StringProperty(required= False)
    turno = db.StringProperty(required= False)
    comision = db.StringProperty(required= False)
    resolutivos = db.StringProperty(required= False)
    enlace = db.StringProperty(required= False)
    diputado = db.ReferenceProperty(Diputado,
                                   required=False,
                                   collection_name='diputado_ini')
    
    def __unicode__(self):
        return self.nombre
            

    
class DiputadoComision(db.Model):
    
    diputado = db.ReferenceProperty(Diputado,
                                   required=True,
                                   collection_name='diputado')
    comision = db.ReferenceProperty(Comision,
                                   required=True,
                                   collection_name='comision')
    titulo = db.StringProperty()