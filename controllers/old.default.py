
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------
# BASEDIR='X:/Video'
# BASEDIR = video_dirs[0]  # 'C:/temp'

# -*- coding: utf-8 -*-
# valid_exts = ['.mp4', '.mpg', '.wmv', '.avi', '.mpeg', '.flv']

# ---- example index page ----
logger.debug('default.py loading')

@auth.requires_login()
def index():
    logger.debug("args: %s vars: %s", str(request.args), str(request.vars))
    if not session.flash_sent:
        session.flash_sent = True
    response.title = T("Progreso")
    response.subtitle = T("Índice")
    session.counter = (session.counter or 0) + 1

    # links = [[x.stem, "visualiza", dict(file=x.name)] for x in p.iterdir() if x.is_file()]
    # links = [
    #     # lambda row: A('', _data_toggle="tooltip", _title="Borrar video del disco",
    #     #               _class='icon trash icon-trash glyphicon glyphicon-trash',
    #     #               _href=URL("default", "borra", args=[row.id], vars=request.vars)),
    #     lambda row: A('', _data_toggle="tooltip", _title="Calcular IGC", _class='fa fa-desktop',
    #                   _href=URL("default", "igc", args=[row.id]))
    #
    #     # oi oi-monitor fas fa-tv  btn btn-primary fa fa-desktop
    # ]
    export_classes = dict(json=False, html=False, tsv=False, xml=False, csv_with_hidden_cols=False,
                          tsv_with_hidden_cols=False)
    lines = int(get_cookie_setting('lines', 18))
    query = (db.peso.id != None)

    grid = SQLFORM.grid(query, user_signature=False, showbuttontext=False,
                        args=request.args[:1], exportclasses=export_classes,
                        paginate=lines, maxtextlengths={'videos.nombre': 110, 'videos.ruta': 70},
                        orderby=~db.peso.fecha)
    # links=links, paginate=10, editable=False, args=request.args[:1], , create=False, deletable=False  deletable=True, create=False, user_signature=False, showbuttontext=False,
    return dict(grid=grid)

@auth.requires_login()
def contorno():
    logger.debug("args: %s vars: %s", str(request.args), str(request.vars))
    if not session.flash_sent:
        session.flash_sent = True
    response.title = T("Progreso")
    response.subtitle = T("Contorno")
    # links = [
    #     lambda row: A('', _data_toggle="tooltip", _title="Calcular IGC", _class='fa fa-desktop',
    #                   _href=URL("default", "igc", args=[row.id]))
    #
    #     # oi oi-monitor fas fa-tv  btn btn-primary fa fa-desktop
    # ]
    export_classes = dict(json=False, html=False, tsv=False, xml=False, csv_with_hidden_cols=False,
                          tsv_with_hidden_cols=False)
    lines = int(get_cookie_setting('lines', 18))
    query = (db.contorno.id != None)

    grid = SQLFORM.grid(query, user_signature=False, showbuttontext=False,
                        args=request.args[:1], exportclasses=export_classes,
                        paginate=lines, maxtextlengths={'videos.nombre': 110, 'videos.ruta': 70},
                        orderby=~db.contorno.fecha)
    # links=links, paginate=10, editable=False, args=request.args[:1], , create=False, deletable=False  deletable=True, create=False, user_signature=False, showbuttontext=False,
    response.view = 'generic.html'
    return dict(grid=grid)

@auth.requires_login()
def pliegues():
    logger.debug("args: %s vars: %s", str(request.args), str(request.vars))
    if not session.flash_sent:
        session.flash_sent = True
    response.subtitle = T("pliegues")
    session.counter = (session.counter or 0) + 1

    # links = [[x.stem, "visualiza", dict(file=x.name)] for x in p.iterdir() if x.is_file()]
    links = [
        # lambda row: A('', _data_toggle="tooltip", _title="Borrar video del disco",
        #               _class='icon trash icon-trash glyphicon glyphicon-trash',
        #               _href=URL("default", "borra", args=[row.id], vars=request.vars)),
        lambda row: A('', _data_toggle="tooltip", _title="Calcular IGC", _class='fa fa-desktop',
                      _href=URL("default", "igc", args=[row.id]))

        # oi oi-monitor fas fa-tv  btn btn-primary fa fa-desktop
    ]
    export_classes = dict(json=False, html=False, tsv=False, xml=False, csv_with_hidden_cols=False,
                          tsv_with_hidden_cols=False)
    lines = int(get_cookie_setting('lines', 18))
    query = (db.igc.id != None)

    grid = SQLFORM.grid(query, user_signature=False, showbuttontext=False,
                        links=links, args=request.args[:1], exportclasses=export_classes,
                        paginate=lines, maxtextlengths={'videos.nombre': 110, 'videos.ruta': 70},
                        orderby=~db.igc.fecha)
    # paginate=10, editable=False, args=request.args[:1], , create=False, deletable=False  deletable=True, create=False, user_signature=False, showbuttontext=False,
    # response.view = 'generic.html'
    return dict(grid=grid)

def get_igc(row):
    if row and row.Adbomen and row.Pectoral and row.Cuadriceps:  # and rows[0].Edad
        nace = date.fromisoformat(get_user_setting('nacimiento', '01/02/1965'))
        edad = (date.today() - nace).days / 365.25
        pliegues = row.Adbomen + row.Pectoral + row.Cuadriceps
        igc_ = 1.10938 - (0.0008267 + 0.0000016) * pliegues - 0.0002574 * edad
        igc_ = 495 / igc_ - 450
        # logger.debug("IGC: %.2f", igc_)
        return igc_
    else:
        return None

@auth.requires_login()
def pliegues_chart():
    logger.debug("args: %s vars: %s", str(request.args), str(request.vars))
    rs = db(db.igc.id != 0)
    rows = rs.select(orderby=db.igc.fecha)
    # session.borra_vars = session.borra_vars or request.vars
    labels = []
    series = {'Adbomen':[], 'Pectoral':[], 'Cuadriceps':[] }
    series_misc = {'igc':[], 'peso':[]}
    if rows:
        for row in rows:
            labels.append(str(row.fecha))
            for serie in series:
                series[serie].append(row[serie])
            series_misc['igc'].append(get_igc(row))
            series_misc['peso'].append(row.Peso_Kg)
    for serie in series_misc:
        series_misc[serie] = str(series_misc[serie])
    for serie in series:
        series[serie] = str(series[serie])
    return dict(labels=labels, series=series, series_misc=series_misc )


#
# @auth.requires_login()
# def edit():
#     logger.debug("args: %s vars: %s", str(request.args), str(request.vars))
#     links = [
#         lambda row: A('', _data_toggle="tooltip", _title="Calcular IGC", _class='fa fa-desktop',
#                       _href=URL("default", "igc", args=[row.id]))
#     ]
#     grid = SQLFORM.grid(db.igc, user_signature=False, links=links)
#     # grid = SQLFORM.grid(db.igc, user_signature=False)
#     return dict(grid=grid)


@auth.requires_login()
def imc():
    logger.debug("args: %s vars: %s", str(request.args), str(request.vars))
    grid = SQLFORM.grid(db.igc, user_signature=False)
    return locals()


@auth.requires_login()
def igc():
    logger.debug("args: %s vars: %s", str(request.args), str(request.vars))
    rs = db(db.igc.id == request.args[0])
    rows = rs.select()
    session.borra_vars = session.borra_vars or request.vars
    if rows and rows[0].Adbomen and rows[0].Pectoral and rows[0].Cuadriceps: # and rows[0].Edad
        nace = date.fromisoformat(get_user_setting('nacimiento', '01/02/1965'))
        edad = (date.today()-nace).days / 365.25
        pliegues = rows[0].Adbomen + rows[0].Pectoral + rows[0].Cuadriceps
        # igc_ = 1.10938 - 0.0008267 * pliegues + 0.0000016 * pliegues - 0.0002574 * edad
        igc_ = 1.10938 - (0.0008267 + 0.0000016) * pliegues - 0.0002574 * edad
        igc_ = 495 / igc_ - 450
        logger.debug("IGC: %.2f", igc_)
        session.flash = f'IGC: {igc_}'
    else:
        session.flash = "Sin datos para calcular IGC"
    redirect(request.env.http_referer)




#
#
# def igc():
#     logger.debug("visualiza args: %s vars: %s", str(request.args), str(request.vars))
#     id = request.args[0]
#     logger.debug("args: %s vars: %s id=%s", str(request.args), str(request.vars), id)
#     visualiza_int(id)
#
#
# def contents():
#     from pathlib import Path
#     from gluon.serializers import json
#     from subprocess import run
#
#     def make_thumb_nail(in_file, out_file, pos_secs=120):
#         # logger.debug("make_thumb_nail i: %s o: %s", in_file,out_file)
#         command = f'ffmpeg -i "{in_file}" -vframes 1 -an -s 548x452 -ss {pos_secs} "{out_file}" '
#         cmd = ['ffmpeg', f'-i "{in_file}"', '-vframes 1', '-an', '-s 548x452', f'-ss {pos_secs}', f'"{out_file}"']
#         logger.debug("make_thumb_nail command: %s", command)
#         logger.debug("make_thumb_nail cmd: %s", cmd)
#         # rc = run(command)  # , shell=True
#         rc = run(command, capture_output=True)  # , shell=True
#         logger.debug("make_thumb_nail rc: %s", str(rc))
#
#         # rows = db(db.videos).select()
#         # if rows:
#         #     response._vars['movies'] = []
#         #     for row in rows:
#         #         fn = Path(row.ruta) / Path(row.nombre)
#
#     # logger.debug("\ncontents\n  args: %s\n  vars: %s", str(request.args), str(request.vars))
#     # logger.debug("\ncontents\n  request: %s", str(request))
#     logger.debug("host remoto: %s", request.env['REMOTE_ADDR'])
#     # id = request.args[0]
#     # rows = db(db.videos.id > -1).select(db.videos.ALL)
#     hide_private = get_global_setting('hide_private', True)
#     if hide_private:
#         rows = db((db.videos.lastscan == True) & (db.videos.private == False)).select()
#     else:
#         rows = db(db.videos.lastscan == True).select()
#     # rows = db(db.videos.id == id).select(db.videos.ALL)
#     response._vars = dict()
#     if rows:
#         response._vars['movies'] = []
#         thumbs_path = Path(request.folder) / 'static' / 'thumbs'
#         rows.exclude(lambda row: 'hide' in row.ruta.lower() or row.nombre[-4:].lower() != '.mp4')
#         for row in rows.sort(lambda row: row.ruta + row.nombre):
#             fn = Path(row.ruta) / row.nombre
#             # if not fn.suffix == '.mp4' or 'hide' in str(row.ruta).lower():
#             #     continue
#             # logger.debug("fn: %s", str(fn))
#             # logger.debug("request.path: %s", request.folder)
#             thumb_path = thumbs_path / f'{row.id}.jpg'
#             # logger.debug("thumbs_path: %s\n  thumb_path: %s", str(thumbs_path), str(thumb_path))
#             movie = dict()
#             movie['id'] = row.id
#             movie['categories'] = [fn.parent.name, 'Todo']
#             movie['channel_id'] = fn.parent.name
#             movie['title'] = fn.stem
#             movie['description'] = 'Video de ' + fn.parent.name
#             movie['videoURL'] = URL('get', args=f'{row.id}.mp4', scheme='http', host=request.env['HTTP_HOST'],
#                                     extension=False)
#             # movie['thumbURL'] = movie['imgURL'] = URL('static', f'thumbs/{row.id}.jpg', scheme='http', host=request.env['HTTP_HOST'], extension=False)
#             movie['thumbURL'] = movie['imgURL'] = URL('static', 'images/fatma.png', scheme='http',
#                                                       host=request.env['HTTP_HOST'], extension=False)
#             response._vars['movies'].append(movie)
#             # if not thumb_path.exists():
#             #     make_thumb_nail(str(fn), str(thumb_path))
#
#     return json(response._vars['movies'])
#     # return response._vars


@auth.requires_login()
def suspend():
    # logger.debug("%s vars: %s", request.args, request.vars)
    # suspend_thread.run()
    from datetime import timedelta as timed
    # logger.debug("request.now: %s", request.now)
    start = request.now + timed(seconds=5)
    rc = scheduler.queue_task('suspend', start_time=start)
    logger.debug("suspend scheduled(%s), redirecting", str(start))
    redirect(request.env.http_referer)

@auth.requires_login()
def options():
    # session.returnto = session.returnto or request.env['HTTP_REFERER']
    logger.debug("Return to: '%s'", session.returnto)
    form = FORM(
        # DIV(
        #     LABEL('Privado oculto', _class='control-label col-sm-2', _for='priv'),
        #     DIV(INPUT(_name='hide_private', _id='priv', _type='checkbox', _class='form-control'),
        #         _class='col-sm-2')),
        DIV(
            LABEL('Líneas', _class='control-label col-sm-2', _for='lines'),
            DIV(INPUT(_name='lines', requires=IS_NOT_EMPTY(), _id='lines', _class='form-control',
                      placeholder="Número de lineas de las tablas"), _class='col-sm-2'),
            _class='form-group'),
        DIV(
            LABEL('Peso Kg', _class='control-label col-sm-2', _for='peso'),
            DIV(INPUT(_name='peso', _id='peso', _class='form-control', requires=IS_NOT_EMPTY()), _class='col-sm-2'),
            _class='form-group'),
        # DIV(
        #     LABEL('Altura cm', _class='control-label col-sm-2', _for='altura'),
        #     DIV(INPUT(_name='altura', _id='altura', _class='form-control', requires=IS_NOT_EMPTY()), _class='col-sm-2'),
        #     _class='form-group'),
        # DIV(
        #     LABEL('Edad', _class='control-label col-sm-2', _for='edad'),
        #     DIV(INPUT(_name='edad', _id='edad', _class='form-control', requires=IS_NOT_EMPTY()) , _class='col-sm-2'),
        #     _class='form-group'),
        DIV(
            LABEL('Nacimiento', _class='control-label col-sm-2', _for='nacimiento'),
            DIV(INPUT(_name='nacimiento', _id='nacimiento', _class='form-control',
                      requires=IS_DATE(format='%d/%m/%Y', error_message='formato: DD/MM/AAAA')), _class='col-sm-2'), #,
            _class='form-group'),
        DIV(DIV(INPUT(_type='submit', _class='btn btn-primary'), _class='col-sm-4'), _class='form-group'),
        # _class='container left'),
        _class="form-horizontal"
    )

    form.vars['lines'] = get_cookie_setting('lines', 18)
    # form.vars['hide_private'] = get_global_setting('hide_private', True)
    # form.vars['altura'] = get_user_setting('altura', 180)
    form.vars['peso'] = get_user_setting('peso', 75)
    # form.vars['edad'] = get_user_setting('edad', 56)
    form.vars['nacimiento'] = get_user_setting('nacimiento', '1965-02-01')
    form.vars['nacimiento'] = date.fromisoformat(form.vars['nacimiento']).strftime('%d/%m/%Y')
    # form.vars['lines'] = get_user_setting('lines', 18) #session.lines
    if form.accepts(request, session, keepvalues=True):
        # response.flash = 'form accepted'
        # try:
        set_cookie_setting('lines', int(form.vars['lines']) or 18)
        # set_global_setting('hide_private', form.vars['hide_private'])
        # set_user_setting('altura', form.vars['altura'] or 180)
        set_user_setting('peso', form.vars['peso'] or 75)
        # set_user_setting('edad', form.vars['edad'] or 56)
        set_user_setting('nacimiento', form.vars['nacimiento'])
        goto = session.returnto or URL('default', 'index')
        session.returnto = None
        redirect(goto)
        # except ValueError as ex:
        #     response.flash = 'Has de introducir un número'

    elif form.errors:
        response.flash = 'Errores'
    else:
        # response.flash = 'Rellena todos los campos'
        session.returnto = session.returnto or request.env['HTTP_REFERER']

    return dict(form=form)


# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status': 'success', 'email': auth.user.email})


# ---- Smart Grid (example) -----
@auth.requires_membership('admin')  # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html'  # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)


#
# # ---- Embedded wiki (example) ----
# def wiki():
#     auth.wikimenu()  # add the wiki to the menu
#     return auth.wiki()
#
#
# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

#
# # ---- action to server uploaded static content (required) ---
# @cache.action()
# def download():
#     """
#     allows downloading of uploaded files
#     http://..../[app]/default/download/[filename]
#     """
#     logger.debug("visualiza args: %s vars: %s", str(request.args), str(request.vars))
#     return response.download(request, db)
