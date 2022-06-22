_DEFAULT_USER= 'global'
# logger.debug("settings.py loading")


# Private functions
def get_settings(user=_DEFAULT_USER):
    #logger.debug("")
    rec = db(db.user_settings.username == user).select().first()
    if not rec:
        settings = {}
        #logger.debug("21")

        db.user_settings.insert(username=user, settings=settings)
        # db.user_settings.insert(username=auth.user.username, settings=json.dumps(settings))
        # db.user_settings.insert(username=auth.user.username)
        db.commit()
    else:
        #logger.debug("22")
        settings = rec.settings or dict()
        # settings = json.loads(rec.settings) or dict()
    return settings


def get_user_settings():
    #logger.debug("")
    #logger.debug("auth.user.username")
    return get_settings(auth.user.username)


def set_settings(settings, user=_DEFAULT_USER):
    
    #logger.debug("settings:%s user:%s", settings, user)
    rec = db(db.user_settings.username == user).select().first()
    # logger.debug("%s: %d recs settings:%s user:%s", __name__, len(rec), settings, user)
    if not rec:
        db.user_settings.insert(username=user, settings=settings)
        #logger.debug("Creando settings para este usuario")
    else:
        rec.update_record(settings=settings)
        #logger.debug("Actualizados los settings para ")
    db.commit()


def set_user_settings(settings):
    set_settings(settings, auth.user.username)


# Public functions
def set_user_setting(setting, value):
    settings = get_user_settings()
    settings[setting] = value
    set_user_settings(settings)
    return


def set_global_setting(setting, value):
    settings = get_settings()
    settings[setting] = value
    set_settings(settings)
    return


def get_user_setting(setting, default_value):
    settings = get_user_settings()
    if not setting in settings:
        set_user_setting(setting, default_value)
        value = default_value
    else:
        value = settings.get(setting)
    return value


def get_global_setting(setting, default_value):
    settings = get_settings()
    if not setting in settings:
        set_global_setting(setting, default_value)
        value = default_value
    else:
        value = settings.get(setting)
    return value


def set_cookie_setting(setting, value):
    response.cookies[setting] = value
    response.cookies[setting]['expires'] = 300 * 24 * 3600
    response.cookies[setting]['path'] = '/' + request.application
    return


def get_cookie_setting(setting, default_value):
    setting = ((setting in request.cookies) and request.cookies[setting].value) or default_value
    return setting
