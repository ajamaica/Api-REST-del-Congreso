
import re
import webapp2
from google.appengine.api import urlfetch
from BeautifulSoup import *
from google.appengine.ext import db
import json as simplejson
import os
from google.appengine.ext.webapp import template

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
    
class MainHandler(webapp2.RequestHandler):
    def get(self):
        template_values = dict()
        path = os.path.join(os.path.dirname(__file__),'templates', 'index.html')
        self.response.out.write(template.render(path, template_values))
        

class IniciativaHandler(webapp2.RequestHandler):
    def get(self,id):
        self.response.write('Hello world!')

class DiputadoHandler(webapp2.RequestHandler):
    def get(self,id):
        url = "http://sitl.diputados.gob.mx/LXII_leg/curricula.php?dipt=%s" % id
        content = urlfetch.fetch(url,deadline=90).content
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
        
        for comision in comisiones:
            com = Comision.get_or_insert(str(comision['href'].replace("integrantes_de_comisionlxii.php?comt=","")))
            com.nombre = comision.text
            com.put()
            relation = DiputadoComision(comision = com,diputado = obj_diputado)
            relation.put()
            
        result = []
        result.append(dict([(p, (unicode(getattr(obj_diputado, p)))) for p in obj_diputado.properties()]))
        self.response.write(simplejson.dumps(  result ))
        

class DiputadosHandler(webapp2.RequestHandler):
    
    def get(self):
        teams = gql_json_parser(Diputado.all().order("nu_diputado")) 
        
        self.response.write(simplejson.dumps( teams ))
    
    def crawl(self):
        
        url = "http://sitl.diputados.gob.mx/LXII_leg/listado_diputados_gpnp.php?tipot="
        content = urlfetch.fetch(url,deadline=90).content
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
                
                #fraccion.put()
                
            if diputado.find("a"):
                
                id_diputado = diputado.find("a")['href'].replace("curricula.php?dipt=","")
                obj_diputado = Diputado.get_or_insert(id_diputado)
                obj_diputado.nombre = diputado.find("a").text[3:].strip()
                obj_diputado.nu_diputado = int(id_diputado)
                obj_diputado.fraccion = fraccion
                obj_diputado.put()
                
                diputados.append({ "nu_diputado" :  obj_diputado.nu_diputado, "diputado" :  obj_diputado.nombre   , "partido" : fraccion.nombre })
                
        self.response.write(simplejson.dumps( diputados ))

class DiputadosCrawlHandler(webapp2.RequestHandler):
    
    
    def get(self):
        
        url = "http://sitl.diputados.gob.mx/LXII_leg/listado_diputados_gpnp.php?tipot="
        content = urlfetch.fetch(url,deadline=90).content
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
                
                #fraccion.put()
                
            if diputado.find("a"):
                
                id_diputado = diputado.find("a")['href'].replace("curricula.php?dipt=","")
                obj_diputado = Diputado.get_or_insert(id_diputado)
                obj_diputado.nombre = diputado.find("a").text[3:].strip()
                obj_diputado.nu_diputado = int(id_diputado)
                obj_diputado.fraccion = fraccion
                obj_diputado.put()
                
                diputados.append({ "nu_diputado" :  obj_diputado.nu_diputado, "diputado" :  obj_diputado.nombre   , "partido" : fraccion.nombre })
                
        self.response.write(simplejson.dumps( diputados ))
        
class DiputadoIniciativaHandler(webapp2.RequestHandler):
    def get(self,id):
        
        for index in range(1,6):
            url = "http://sitl.diputados.gob.mx/LXII_leg/iniciativas_por_pernplxii.php?iddipt=%s&pert=%i" % (id,index)
            content = urlfetch.fetch(url,deadline=90).content
            soup = BeautifulSoup(content)
            dumped = soup.findAll("table")[1]
            for t in dumped.contents[2:]:
                if t.__class__.__name__ == "Tag" and len(t.findAll("td"))>0:
                    primer_bloque = t.findAll("td")[0]
                    segundo_bloque = t.findAll("td")[1]
                    tercer_bloque = t.findAll("td")[2]
                    cuarto_bloque = t.findAll("td")[3]
                    self.response.write("Primer : %s <br><br> Segundo : %s <br><br> Tercero : %s  <br><br> Cuarto :%s"% (primer_bloque,segundo_bloque,tercer_bloque,cuarto_bloque))
                else:
                    # TODO: Esta mal formateado el HTML asi que unas cosas las encuentro como String no como TAG. QUE MALA Pagina
                    # self.response.write(t)
                    pass
            
            
            

class DiputadoProposicionesHandler(webapp2.RequestHandler):
    def get(self,id):
        
        for index in range(1,6):
            url = "http://sitl.diputados.gob.mx/LXII_leg/proposiciones_por_pernplxii.php?iddipt=%s&pert=%i" % (id,index)
            content = urlfetch.fetch(url,deadline=90).content
            soup = BeautifulSoup(content)
            dumped = soup.findAll("table")[1]
            if dumped.findAll("tr")[1] :
                cells = dumped.findAll("tr")[1].findAll("td")
                if len(cells) :
                    iniciativa = Iniciativa.get_or_insert(cells[0].contents[0].text.split('&nbsp;')[1])
                    iniciativa.nombre = cells[0].contents[0].text.split('&nbsp;')[1]
                    iniciativa.turno = cells[4].findAll('span',{'class':'Estilo71'})[1].find('a').text
                    iniciativa.resolutivos = cells[4].findAll('span',{'class':'Estilo71'})[0].text
                    iniciativa.enlace = cells[4].findAll('span',{'class':'Estilo71'})[1].find('a')["href"] 
                    iniciativa.diputado = Diputado.get_or_insert(id)
                    iniciativa.put()
                    
                    result = []
                    result.append(dict([(p, (unicode(getattr(iniciativa, p)))) for p in iniciativa.properties()]))
                    
        self.response.write(simplejson.dumps(result))
            
class DiputadoVotacionesHandler(webapp2.RequestHandler):
    def get(self,id):
        
        votaciones = dict()
        for index in range(1,6):
            url = "http://sitl.diputados.gob.mx/LXII_leg/votaciones_por_pernplxii.php?iddipt=%s&pert=%i" % (id,index)
            content = urlfetch.fetch(url,deadline=90).content
            soup = BeautifulSoup(content)
            dumped = soup.findAll("table")[0].findAll("table")[1]
            tr = dumped.findAll("tr")[3:]
            fecha = ""
            if tr:
                for row in tr :
                    if (len(row.contents)) == 1 and  row.contents[0] != "\n" :
                        fecha = row.contents[0]
                        votaciones[fecha.text] = list()
                    
                    if (len(row.contents)) == 9:
                        data = [item.text for item in row.contents if item != "\n" and item.text != "&nbsp;" ]
                        votaciones[fecha.text].append({"id_dia":data[0],"titulo":data[1], "sentido":data[2]})
                        
        self.response.write(simplejson.dumps( votaciones ))

class DiputadoAsistenciasHandler(webapp2.RequestHandler):
    def get(self,id):
        
        asistencias = dict()
        for index in range(1,6):
            url = "http://sitl.diputados.gob.mx/LXII_leg/asistencias_por_pernplxii.php?iddipt=%s&pert=%i" % (id,index)
            content = urlfetch.fetch(url,deadline=90).content
            soup = BeautifulSoup(content)
            dumped = soup.findAll("table")[0]
            for mes in dumped.findAll("table")[5].findAll("table"):
                mes_txt = mes.find("span", {"class" : "TitulosVerde"})
                if mes_txt:
                    asistencias[mes_txt.text] = list()
                    for dia in mes.findAll("td",{"bgcolor" : "#D6E2E2"}):
                        asistencias[mes_txt.text].append({"dia": dia.find("font").contents[0], "estado" : dia.find("font").contents[2]})
        del asistencias[""]
        self.response.write(simplejson.dumps(asistencias ))
                
            
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/iniciativa/(\d+)$', IniciativaHandler),
    ('/diputado/$', DiputadosHandler),
    ('/diputado/crawl$', DiputadosCrawlHandler),
    ('/diputado/(\d+)$', DiputadoHandler),
    ('/diputado/(\d+)/iniciativas$', DiputadoIniciativaHandler),
    ('/diputado/(\d+)/proposiciones$', DiputadoProposicionesHandler),
    ('/diputado/(\d+)/votaciones$', DiputadoVotacionesHandler),
    ('/diputado/(\d+)/asistencias$', DiputadoAsistenciasHandler),
], debug=True)
