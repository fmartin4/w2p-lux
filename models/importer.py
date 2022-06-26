from pathlib import Path
import xlrd
from glob import glob
import os
import datetime

_server =['https://', 'api.esios.ree.es', '/archives/71/download?date_type=datos&end_date=_end_T23%3A59%3A59%2B00%3A00&locale=es&start_date=_start_T00%3A00%3A00%2B00%3A00']

_tmp_dir = 'OS' in os.environ and 'Windows' in os.environ['OS'] and 'c:/temp' or '/tmp'
_tmp_zip =      _tmp_dir + '/luz.zip'
_tmp_xls_dir =  _tmp_dir + '/PVPC'
_tmp_csv =      _tmp_dir + '/lux.csv'

def import_file(file_name: str ):
    wb = xlrd.open_workbook(file_name)
    sh = wb.sheet_by_name('Tabla de Datos PCB')
    logger.debug('Importando %s, %d filas', file_name, sh.nrows)
    # your_csv_file = open('your_csv_file.csv', 'w')
    # wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)
    on = False
    table = []
    header = []
    for rownum in range(sh.nrows):
        vals = sh.row_values(rownum)
        # logger.debug(str(vals))
        if not vals[0] :
            on = False
        if on:
            table += [vals[:7]]
        if vals[0] == 'Día':
            header = vals[:7]
            on = True
    return table, header

def unzip():
    logger.debug('Unzip %s to %s', _tmp_zip, _tmp_xls_dir)
    from zipfile import ZipFile
    try:
        with ZipFile(_tmp_zip) as myzip:
            myzip.extractall(_tmp_xls_dir)
    except Exception as ex:
        logger.error("error '%s' with %s on %s", ex.args, _tmp_zip, _tmp_xls_dir )


def getWebPage(start, end, out_file):
    import http.client

    args = _server[2].replace('_start_', start).replace('_end_', end)
    try:
        conn = http.client.HTTPSConnection(_server[1])
        conn.request("GET", args)
        r1 = conn.getresponse()
        logger.debug("getWebPage %s %s", r1.status, r1.reason)
        with open(out_file, 'bw') as out:
            while chunk := r1.read(200):
                # print(repr(chunk))
                out.write(chunk)

    except Exception as ex:
        logger.error("error '%s'", ex.args)


def last_date_imported():
    rows = db(db.precio).select()
    row = rows.last()
    if row:
        logger.debug("time %s PVPC %f Peaje %s", row.momento, row.PVPC, row.Peaje)
        return row.momento
    else:
        return datetime.datetime.now()

def tbl2db(table :list):
    # create xls dir if not exists
    tzone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
    for rec in table:
        Peaje=rec[2]
        PVPC=rec[4]
        time = rec[0] - 25569 # Mocosoft empieza en 1900, epoch en 1970
        # viene fecha y hora+1, supuestamente en localtime. hay que restar 1 y pasar a UTC
        time_local = datetime.datetime.fromtimestamp(time * 24 * 3600, tz=tzone)
        time_local += datetime.timedelta(hours=rec[1 ] -1)
        utc_offset = time_local.replace(tzinfo=datetime.timezone.utc ) -time_local.astimezone(datetime.timezone.utc)
        time_local -= utc_offset
        db.precio.update_or_insert(db.precio.momento == time_local, momento=time_local, Peaje=Peaje ,PVPC=PVPC)
        # rs = db((db.precio.time == time_local))
        # dbrecs = rs.select()
        # dbrec = dbrecs.first()
        # if dbrec:
        #     dbrec.update_record(Peaje=Peaje ,PVPC=PVPC)  # rec.update_record(**args)
        #     logger.debug(f'update {time_local}')
        # else:
        #     db.precio.insert(time=time_local, Peaje=Peaje ,PVPC=PVPC)
        #     logger.debug(f'insert {time_local}')
    db.commit()
    return True

def import_xls():
    # create xls dir if not exists
    _tmp_xls_path = Path(_tmp_xls_dir)
    if not _tmp_xls_path.exists():
        _tmp_xls_path.mkdir()
        logger.debug("Creado %s", _tmp_xls_dir)
    files = glob(_tmp_xls_dir +'/*.xls')
    # tbl = []
    for file in files:
        table, header = import_file(file)
        # tbl += table
        if tbl2db(table):
            path = Path(file)
            bak = path.with_suffix('.bak')
            if(bak.exists()):
                bak.unlink()
            path.rename(bak)
            logger.info('Importado %s y renombrando a %s', path, bak)

    # ptbl = Table(header)
    # ptbl.setTable([header]+tbl)
    # ptbl.dumpCsv(_tmp_csv)

def get_auto_dates():
    # create xls dir if not exists
    # last_ts = last_date_imported( ) /1000
    last = last_date_imported()
    logger.debug('Last imported: %s', last)
    # LOCAL_TIMEZONE = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
    # last_ts = datetime.datetime.fromtimestamp(last_ts, tz=LOCAL_TIMEZONE)
    # last_ts += datetime.timedelta(days=1)
    end = datetime.datetime.now()
    # end_ts = end.timestamp()
    str_start = (last + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    str_end = end.strftime('%Y-%m-%d')

    return str_start, str_end


def entre_fechas(fecha1: str, fecha2: str):
    logger.info('Descargar datos entre %s y %s', fecha1, fecha2)
    if fecha1 == fecha2:
        getWebPage(fecha1, fecha2, _tmp_xls_dir + '/' + fecha2 + '.xls')
    else:
        getWebPage(fecha1, fecha2, _tmp_zip)
        unzip()
    import_xls()

def auto_import_silent():
    str_start, str_end = get_auto_dates();
    if str_end < str_start:
        logger.info('Sin datos mas nuevos que %s', str_start)
        return "Sin datos mas nuevos que %s" % str_start
        # redirect(request.env['HTTP_REFERER'])
    entre_fechas(str_start, str_end)
    return f"Importado entre {str_start} y {str_end}"
