# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# AppConfig configuration made easy. Look inside private/appconfig.ini
# Auth is for authenticaiton and access control
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig
from gluon.tools import Auth
from gluon.scheduler import Scheduler
from pathlib import Path
import logging
import locale
import datetime #import date

# locale.setlocale(locale.LC_ALL, 'Spanish')


def initLog(level=logging.DEBUG, logfile=None, format='%(asctime)s %(levelname)-8s %(funcName)s: %(message)s'):
    """Inicializa el logging.

    Args:
      level (int, optional):
        Nivel de información, por defecto DEBUG.
      logfile (str, optional):
        Si se especifica,será el nombre del fichero donde se volcará el log.
    Returns:
    """
    mainlog = logging.getLogger()
    mainlog.setLevel(logging.WARNING) # DEBUG
    fm4log = logging.getLogger("web2py.app.discat")
    fm4log.setLevel(level)

    # while len(fm4log.handlers) > 0:
    #     fm4log.removeHandler(fm4log.handlers[0])

    # create file handler which logs even debug messages
    if logfile:
        fh = logging.FileHandler(logfile)
        # fh.setFormatter(formatter)
        fm4log.addHandler(fh)

    for handler in mainlog.handlers:
        handler.setFormatter(logging.Formatter(format))
    # # create console handler with a higher log level
    # ch = logging.StreamHandler()
    # ch.setFormatter(formatter)
    # # add the handlers to the logger
    # fm4log.addHandler(ch)
    return fm4log

#
def suspend_int():
    logger.debug("suspend_int ordered")
#     from subprocess import run
#     rc = run('cmd /c shut --suspend 2s', capture_output=True)   # , shell=True
#     if rc.returncode:
#         logger.error( f'Error: {rc}"')
#     logger.debug("suspend_int ended")

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

if request.global_settings.web2py_version < "2.15.5":
    raise HTTP(500, "Requires web2py 2.15.5 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
configuration = AppConfig(reload=True)

if configuration.get('app.production'):
    logger = initLog(logging.INFO)
else:
    logger = initLog(logging.DEBUG)

logger.info('%s by %s, producción: %s %s', configuration.get('app.name'), configuration.get('app.author')
            , str(configuration.get('app.production')), configuration.get('app.description'))

if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    db = DAL(configuration.get('db.uri'),
             pool_size=configuration.get('db.pool_size'),
             migrate_enabled=configuration.get('db.migrate'),
             check_reserved=['all'])
else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL('google:datastore+ndb')
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------
# logger.debug('DB setup')

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = [] 
if request.is_local and not configuration.get('app.production'):
    response.generic_patterns.append('*')

# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = 'bootstrap4_inline'
response.form_label_separator = ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db, host_names=configuration.get('host.names'))

# -------------------------------------------------------------------------
# create all tables needed by auth, maybe add a list of extra fields
# -------------------------------------------------------------------------
auth.settings.extra_fields['auth_user'] = []
auth.define_tables(username=True, signature=False)

# logger.debug('AUTH1 setup')

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else configuration.get('smtp.server')
mail.settings.sender = configuration.get('smtp.sender')
mail.settings.login = configuration.get('smtp.login')
mail.settings.tls = configuration.get('smtp.tls') or False
mail.settings.ssl = configuration.get('smtp.ssl') or False
# logger.debug('MAIL setup')

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
# logger.debug('AUTH2 setup')

# -------------------------------------------------------------------------  
# read more at http://dev.w3.org/html5/markup/meta.name.html               
# -------------------------------------------------------------------------
response.meta.author = configuration.get('app.author')
response.meta.description = configuration.get('app.description')
response.meta.keywords = configuration.get('app.keywords')
response.meta.generator = configuration.get('app.generator')
response.show_toolbar = configuration.get('app.toolbar')

# -------------------------------------------------------------------------
# your http://google.com/analytics id                                      
# -------------------------------------------------------------------------
response.google_analytics_id = configuration.get('google.analytics_id')

# -------------------------------------------------------------------------
# maybe use the scheduler
# -------------------------------------------------------------------------

def task_add(a, b):
    return a + b


if configuration.get('scheduler.enabled'):
    from gluon.scheduler import Scheduler
    scheduler = Scheduler(db, heartbeat=configuration.get('scheduler.heartbeat'))
    # tasks = db(db.scheduler_run.run_status != 'COMPLETED').select()
    # for task in tasks:
    #     logger.debug('task %s', str(task))
    #
    #
    # scheduler = Scheduler(db, tasks=dict(demo1=task_add))
    # scheduler.queue_task('demo1', pvars=dict(a=1, b=2), repeats=0, period=180)

# logger.debug('Scheduler setup')

# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
    # >>> db.mytable.insert(myfield='value')
    # >>> rows = db(db.mytable.myfield == 'value').select(db.mytable.ALL)
    # >>> for row in rows: print row.id, row.myfield
#db.files.drop()
sizef = lambda x, row: \
    locale.format_string('%.2f GB', x/1e9, True) if x>1e9\
        else locale.format_string('%.2f MB', x/1e6, True) if x>1e6\
        else locale.format_string('%d', x, True)

db.define_table('precio',
                Field('momento', 'datetime',
                      represent=(lambda x, row: x.strftime('%Y-%m-%d %H:%M:%S') if x else '') ,
                      required=True),
                      # default=(lambda: date.today())),
                # Field('dia','date'),
                # Field('hora', 'integer'),
                # Field.Virtual('dia', lambda row: row.precio.momento.date()),
                # Field.Virtual('hora', lambda row: row.precio.momento.time().hour),
                Field('PVPC', 'double',
                      represent=(lambda x, row: '%.1f' % x ),
                      default=(lambda : get_user_setting('peso', 75)),
                      required=True),
                Field('Peaje', 'string', length=8),
                Field('id', listable=False),
                # redefine=True, # migrate='videos.table',  fake_migrate=True,
                format='%(fecha)s'
                )
# db.precio.day =  Field.Method(lambda row:row.time.date())
# db.precio.hour =  Field.Method(lambda row:row.time.time().hour)

db.define_table('user_settings',
                Field('username', 'string', length=64, required=True),
                Field('settings', 'json', required=True),
                format='%(username)s')
#
# def recuerda_peso(callback, set, new_data):
#     logger.debug('set: %s, new:%s', str(set), str(new_data))
#     if not 'Kg' in new_data:
#         return
#     rows = set.select()
#     for row in rows:
#         try:
#             if row.Kg != new_data.Kg:
#                 set_user_setting('peso', new_data.Kg or 75)
#                 logger.debug("%s: '%s'->'%s'", callback, row.Kg, new_data.Kg)
#         except AttributeError as ex:
#             logger.error("AttributeError %s: '%s''", str(ex), str(row))
#         except Exception as ex:
#             logger.error("%s: '%s''", str(ex), str(row))
#
# def recuerda_peso_ins(new_data):
#     logger.debug('new:%s',  str(new_data))
#     if not 'Kg' in new_data:
#         return
#     set_user_setting('peso', new_data.Kg or 75)
#
# db.peso._before_update.append(lambda s, f: recuerda_peso('recuerda_peso', s, f))
# db.peso._before_insert.append(lambda f: recuerda_peso_ins(f))
# # db.videos._before_delete.append(lambda s: video_delete('before_delete', s))
db.commit()

# logger.debug('DB tables setup')

# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
auth.enable_record_versioning(db)


# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------

# scheduler = Scheduler(db, tasks=dict(suspend=suspend_int))
# logger.debug('db.py done')
