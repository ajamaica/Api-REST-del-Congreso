#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import re
import webapp2
from google.appengine.api import urlfetch
from BeautifulSoup import *
from google.appengine.ext import db
import json as simplejson

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
    

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

class IniciativaHandler(webapp2.RequestHandler):
    def get(self,id):
        self.response.write('Hello world!')

class DiputadoHandler(webapp2.RequestHandler):
    def get(self,id):
        url = "http://sitl.diputados.gob.mx/LXII_leg/curricula.php?dipt=%s" % id
        content = urlfetch.fetch(url,deadline=90,headers = { 'Cache-Control': 'no-cache,max-age=0', 'Pragma': 'no-cache' }).content
        soup = BeautifulSoup(content)
        dumped = soup.find("table").findAll("tr")[2].findAll("table")[1]
        
        entidad_n =  dumped.findAll("tr")[2].text.split(":")[1]
        tipo_de_eleccion = dumped.findAll("tr")[1].text.split(":")[1]
        distrito =  dumped.findAll("tr")[3].text.split(":")[1]
        cabecera = dumped.findAll("tr")[4].text.split(":")[1]
        curul = dumped.findAll("tr")[5].text.split(":")[1]
        suplente =  dumped.findAll("tr")[6].text.split(":")[1]
        onomastico = dumped.findAll("tr")[7].text.split(":")[1]
        email = dumped.findAll("tr")[8].text.split(":")[1]
        comisiones = soup.find("table").findAll("a",{"href" : re.compile("integrantes_de_comisionlx")})
        
        
        obj_diputado = Diputado.get_or_insert(str(id))
        entidad = Entidad.get_or_insert(entidad_n)
        entidad.nombre = entidad_n
        entidad.put()
        
        obj_diputado.entidad = entidad
        obj_diputado.tipo_de_eleccion = tipo_de_eleccion
        obj_diputado.distrito = int(distrito)
        obj_diputado.cabecera =  cabecera
        obj_diputado.curul =  curul
        obj_diputado.suplente = suplente
        obj_diputado.onomastico = onomastico
        obj_diputado.email  = email
        obj_diputado.put()
        result = []
        result.append(dict([(p, (unicode(getattr(obj_diputado, p)))) for p in obj_diputado.properties()]))
        #self.response.write(simplejson.dumps(  result ))
        self.response.write("%s" % comisiones)
        

class DiputadosHandler(webapp2.RequestHandler):
    def get(self):
        url = "http://sitl.diputados.gob.mx/LXII_leg/listado_diputados_gpnp.php?tipot="
        content = urlfetch.fetch(url,deadline=90,headers = { 'Cache-Control': 'no-cache,max-age=0', 'Pragma': 'no-cache' }).content
        soup = BeautifulSoup(content)
        dumped = soup.find("table").findAll("table")[1].findAll("tr")

        diputados = list(dict())
        fraccion =  Fraccion()
        indexP = 0
        
        for diputado in dumped:
            
            if diputado.find("img"):
                if diputado.find("img")['src'] == 'images/pri01.png':
                    fraccion =  Fraccion.get_or_insert("PRI", nombre ="PRI")
                
                if diputado.find("img")['src'] == 'images/pan.png':
                    fraccion =  Fraccion.get_or_insert("PAN", nombre ="PAN")
                
                if diputado.find("img")['src'] == 'images/prd01.png':
                    fraccion =  Fraccion.get_or_insert("PRD", nombre ="PRD")
                
                if diputado.find("img")['src'] == 'images/logvrd.jpg': 
                    fraccion =  Fraccion.get_or_insert("VERDE", nombre ="Verde")
                
                if diputado.find("img")['src'] == 'images/logo_movimiento_ciudadano.png': 
                    fraccion =  Fraccion.get_or_insert("MOVCI", nombre ="Movimiento Ciudadano")

                if diputado.find("img")['src'] == 'images/logpt.jpg': 
                    fraccion =  Fraccion.get_or_insert("PT", nombre ="PT")
                
                if diputado.find("img")['src'] == 'images/panal.gif': 
                    fraccion =  Fraccion.get_or_insert("PANAL", nombre ="PANAL")
                
                fraccion.put()
                
            if diputado.find("a"):
                
                id_diputado = diputado.find("a")['href'].replace("curricula.php?dipt=","")
                obj_diputado = Diputado.get_or_insert(id_diputado)
                obj_diputado.nombre = diputado.find("a").text[3:].strip()
                obj_diputado.nu_diputado = int(id_diputado)
                obj_diputado.fraccion = fraccion
                obj_diputado.put()
                
                diputados.append({ "nu_diputado" :  obj_diputado.nu_diputado, "diputado" :  obj_diputado.nombre   , "partido" : fraccion.nombre })
                
        self.response.write(simplejson.dumps( diputados ))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/iniciativa/(\d+)$', IniciativaHandler),
    ('/diputado/$', DiputadosHandler),
    ('/diputado/(\d+)$', DiputadoHandler)
], debug=True)
