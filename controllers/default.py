# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------
# logger.debug('default.py loading')
#

# ---- example index page ----
import datetime


@auth.requires_login()
def index():
    # logger.debug("args: %s vars: %s", str(request.args), str(request.vars))
    if not session.flash_sent:
        session.flash_sent = True
    response.title = T("Lux")
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

    query = (db.precio.id)
    grid = SQLFORM.grid(query, user_signature=False, showbuttontext=False, args=request.args[:1],
                        exportclasses=export_classes, paginate=lines, orderby=(~db.precio.dia|db.precio.hora))
    # , maxtextlengths={'videos.nombre': 110, 'videos.ruta': 70} links=links, paginate=10, editable=False,
    #  args=request.args[:1], , create=False, deletable=False  deletable=True, create=False, user_signature=False,
    #  showbuttontext=False,
    return dict(grid=grid)


@auth.requires_membership('admin')  # can only be accessed by members of admin groupd
def media_diaria():
    # rows = db(db.precio).select()
    # for row in rows:
    #     row.update_record(dia=row.momento.date(), hora=row.momento.time().hour)
    # db.commit()
    response.view = 'generic.html'  # use a generic view
    # logger.debug("args: %s vars: %s", str(request.args), str(request.vars))
    # export_classes = dict(csv=True, json=False, html=False, tsv=False, xml=False, csv_with_hidden_cols=False,
    #                       tsv_with_hidden_cols=False)
    # lines = int(get_cookie_setting('lines', 18))

    # media = db.precio.PVPC.avg()
    #
    # q = db(db.precio).select(db.precio.dia, db.precio.PVPC.avg(), groupby=db.precio.dia)
    # # return q
    query = (db.precio.id)
    grid = SQLFORM.grid(query, fields=[db.precio.dia, db.precio.PVPC],
                        groupby=db.precio.dia)  # , args=[tablename], deletable=False, editable=False query
    # query = (db.precio.id)
    # grid = SQLFORM.grid(query, args=request.args[:1], exportclasses=export_classes, paginate=lines,
    #                     orderby=~db.precio.momento) # user_signature=False, showbuttontext=False,
    return dict(grid=grid)


def fromisoformat(date_str: str):
    # logger.debug('date_str: "%s" type:%s', date_str, type(date_str))
    if type(date_str) != type(''):
        return date_str
    try:
        from datetime import date
        # logger.debug('date imported')
        # a partir de pyhton 3.7... no me vale en la raspberry... fromisoformat(nace)
        date_list = date_str.split('-')
        # logger.debug('date_list 1' )
        # logger.debug('date_list 1: %s', str(date_list) )
        date_list = [int(x) for x in date_str.split('-')]
        # logger.debug('date_list 2: %s', str(date_list))
        return date(*date_list)
    except Exception as ex:
        logger.error(str(ex))

    return None

@auth.requires_login()
def peso_chart():
    logger.debug("args: %s vars: %s", str(request.args), str(request.vars))
    rs = db(db.peso.id != 0)
    rows = rs.select(orderby=db.peso.fecha)
    # session.borra_vars = session.borra_vars or request.vars
    labels = []
    series = {'peso': []}
    if rows:
        for row in rows:
            labels.append(str(row.fecha))
            series['peso'].append(row.Kg)
    for serie in series:
        series[serie] = str(series[serie])
    return dict(labels=labels, charts=[series])


@auth.requires_login()
def precio_chart():
    DAYS=7
    logger.debug("args: %s vars: %s", str(request.args), str(request.vars))
    if (len(request.args) == 1 and request.args[0] == 'peso'):
        d = peso_chart()
        logger.debug("Graficas de peso: %s", str(d))
        return d

    rows = db(db.precio.dia>datetime.datetime.now()-datetime.timedelta(days=DAYS)).select(orderby=(db.precio.dia|db.precio.hora))
    if not rows:
        return 'Sin filas a mostrar en los dos últimos días'

    # session.borra_vars = session.borra_vars or request.vars
    labels = str([x for x in range(24)])  # Las x son las 24 horas del día
    fechas = db(db.precio.dia>datetime.datetime.now()-datetime.timedelta(days=DAYS)).select(db.precio.dia, groupby=db.precio.dia)
    series1 = dict()
    for fecha in fechas:
        series1[str(fecha.dia)] = [0 for x in range(24)]       # Los días son las series, ubicamos 24 huecos
    # series2 = {'igc': [], 'peso': []}
    for row in rows:
        # labels.append(str(row.dia))
        str_dia = str(row.dia)
        # logger.debug("str_dia: %s, hora: %d, PVPC:%d", str_dia,row.hora,row.PVPC)
        series1[str_dia][row.hora] = row.PVPC
        # for serie in series1:
        #     series1[serie].append(row[serie])
        # series2['igc'].append(get_igc(row))
        # series2['peso'].append(row.Peso_Kg)
    # for serie in series2:
    #     series2[serie] = str(series2[serie])
    for serie in series1:
        series1[serie] = str(series1[serie])    # forma cutre de JSONizar la lista
    return dict(title='PVPC por días',labels=labels, charts=[series1])

@auth.requires_login()
def options():
    # session.returnto = session.returnto or request.env['HTTP_REFERER']
    # returnto = session.returnto or request.env.http_referer
    # logger.debug("1")
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
                      requires=IS_DATE(format='%d/%m/%Y', error_message='formato: DD/MM/AAAA')), _class='col-sm-2'),
            # ,
            _class='form-group'),
        DIV(DIV(INPUT(_type='submit', _class='btn btn-primary'), _class='col-sm-4'), _class='form-group'),
        # _class='container left'),
        _class="form-horizontal"
    )
    # logger.debug("2")

    form.vars['lines'] = get_cookie_setting('lines', 18)
    # logger.debug("3")
    # form.vars['hide_private'] = get_global_setting('hide_private', True)
    # form.vars['altura'] = get_user_setting('altura', 180)
    form.vars['peso'] = get_user_setting('peso', 75)
    # logger.debug("4")
    # form.vars['edad'] = get_user_setting('edad', 56)
    # form.vars['nacimiento'] = get_user_setting('nacimiento', '1965-02-01')
    form.vars['nacimiento'] = fromisoformat(get_user_setting('nacimiento', '1965-02-17')).strftime('%d/%m/%Y')
    # logger.debug("7: %s", form.vars['nacimiento'])
    # form.vars['lines'] = get_user_setting('lines', 18) #session.lines
    if form.accepts(request, session, keepvalues=True):
        # logger.debug("form.accepts, 1 will go to %s", session.returnto)
        # response.flash = 'form accepted'
        # try:
        set_cookie_setting('lines', int(form.vars['lines']) or 18)
        # set_global_setting('hide_private', form.vars['hide_private'])
        # set_user_setting('altura', form.vars['altura'] or 180)
        set_user_setting('peso', form.vars['peso'] or 75)
        # set_user_setting('edad', form.vars['edad'] or 56)
        # logger.debug("set nacimiento: %s", form.vars['nacimiento'])
        set_user_setting('nacimiento', str(form.vars['nacimiento']))
        goto = session.returnto or URL('default', 'index')
        # logger.debug("form.accepts, 2 will go to %s", goto)
        goto = 'default/options' in goto and URL('default', 'index') or goto
        # logger.debug("form.accepts, 3 will go to %s", goto)
        session.returnto = None
        redirect(goto)
        # except ValueError as ex:
        #     response.flash = 'Has de introducir un número'

    elif form.errors:
        # logger.debug("form.errors")
        response.flash = 'Errores'
    else:
        # logger.debug("form.else (ni errores ni aceptado aun)")
        # response.flash = 'Rellena todos los campos'
        prev = session.returnto
        session.returnto = session.returnto or request.env['HTTP_REFERER']
        # logger.debug("form.else (ni errores ni aceptado aun), retono a %s->%s", prev, session.returnto)

    return dict(form=form)


#
# @auth.requires_login()
# def index2():
#     response.flash = T("Hello World")
#     return dict(message=T('Welcome to web2py!'))
#
#
# # ---- API (example) -----
# @auth.requires_login()
# def api_get_user_email():
#     if not request.env.request_method == 'GET': raise HTTP(403)
#     return response.json({'status': 'success', 'email': auth.user.email})
#

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
#     return response.download(request, db)
