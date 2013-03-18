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
    
class FraccionP(Object):
    pass

        
class ComisionP(Object):
    pass



class EntidadP(Object):
    pass

    
class DiputadoP(Object):
    pass

class IniciativaP(Object):
    pass

    