

@auth.requires_login()
def auto_import():
    auto_import_silent()
    redirect(request.env['HTTP_REFERER'])


@auth.requires_login()
def date_range():
    # session.returnto = session.returnto or request.env['HTTP_REFERER']
    # returnto = session.returnto or request.env.http_referer
    # logger.debug("1")
    form = FORM(
        DIV(
            LABEL('Inicio', _class='control-label col-sm-2', _for='Inicio'),
            DIV(INPUT(_name='Inicio', _id='Inicio', _class='form-control',
                      requires=IS_DATE(format='%d/%m/%Y', error_message='formato: DD/MM/AAAA')), _class='col-sm-2'),
            # ,
            _class='form-group'),
        DIV(
            LABEL('Fin', _class='control-label col-sm-2', _for='Fin'),
            DIV(INPUT(_name='Fin', _id='Fin', _class='form-control',
                      requires=IS_DATE(format='%d/%m/%Y', error_message='formato: DD/MM/AAAA')), _class='col-sm-2'),
            # ,
            _class='form-group'),
        DIV(DIV(INPUT(_type='submit', _class='btn btn-primary'), _class='col-sm-4'), _class='form-group'),
        # _class='container left'),
        _class="form-horizontal"
    )
    # logger.debug("2")

    form.vars['Inicio'] = datetime.datetime.now().date().strftime('%d/%m/%Y')
    form.vars['Fin'] = datetime.datetime.now().date().strftime('%d/%m/%Y')
    # logger.debug("7: %s", form.vars['nacimiento'])
    # form.vars['lines'] = get_user_setting('lines', 18) #session.lines
    if form.accepts(request, session, keepvalues=True):
        logger.debug("form.accepts, 1 will go to %s", session.returnto)
        f1, f2 = form.vars['Inicio'].strftime('%Y-%m-%d'), form.vars['Fin'].strftime('%Y-%m-%d')
        entre_fechas(f1, f2)
        goto = session.returnto or URL('default', 'index')
        session.returnto = None
        redirect(goto)
        # except ValueError as ex:
        #     response.flash = 'Has de introducir un número'

    elif form.errors:
        # logger.debug("form.errors")
        response.flash = 'Errores'
    else:
        logger.debug("form.else (ni errores ni aceptado aun)")
        # response.flash = 'Rellena todos los campos'
        prev = session.returnto
        session.returnto = session.returnto or request.env['HTTP_REFERER']
        # logger.debug("form.else (ni errores ni aceptado aun), retono a %s->%s", prev, session.returnto)
    response.view = 'generic.html'  # use a generic view
    return dict(form=form)

def croned():
    logger.debug('cron order')
    res = auto_import_silent()
    # with open(r'c:\temp\kk.log','a+') as log:
    #     log.writelines(['%s log' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), res])
