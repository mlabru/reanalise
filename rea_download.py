# -*- coding: utf-8 -*-
"""
faz o download dos dados para reanalise
"""
# < imports >--------------------------------------------------------------------------

# python library
import datetime
import os
import sys

# CDS API
import cdsapi

# < global data >----------------------------------------------------------------------

# wait time
DI_WAIT = 30
# pressão
DLST_PRESSAO = [ "850", "1000" ]
# variáveis
DDCT_VARS = {    "850": ["temperature", "u_component_of_wind", "v_component_of_wind"],
                "1000": ["relative_humidity"],
              "single": ["10m_u_component_of_wind", "10m_v_component_of_wind",
                         "2m_dewpoint_temperature", "2m_temperature",
                         "cloud_base_height", "instantaneous_10m_wind_gust",
                         "mean_sea_level_pressure", "surface_pressure",
                         "total_cloud_cover", "total_precipitation" ] }

# -------------------------------------------------------------------------------------
def build_template(fs_vars: str, fs_ano: str, fs_mes: str, flst_dias: list):
    """
    build template
    """
    # build template
    ldct_tmpl = { "product_type": "reanalysis",
                  "format": "netcdf",
                  "year": fs_ano,
                  "month": fs_mes,
                  "day": flst_dias,
                  "time": ["00:00", "01:00", "02:00",
                           "03:00", "04:00", "05:00",
                           "06:00", "07:00", "08:00",
                           "09:00", "10:00", "11:00",
                           "12:00", "13:00", "14:00",
                           "15:00", "16:00", "17:00",
                           "18:00", "19:00", "20:00",
                           "21:00", "22:00", "23:00"],
                  "variable": DDCT_VARS[fs_vars],
                  "area": [10, -90, -60, -30] }

    # return template
    return ldct_tmpl

# -------------------------------------------------------------------------------------
def cria_arquivo_ok(fs_name: str):
    """
    cria um arquivo "sentinela"
    """
    try:
        # abre o arquivo em modo de escrita
        with open(fs_name + ".ok", 'w') as lfh:
            # just write nothing
            lfh.write("\n")

        # log
        print(f"Arquivo '{fs_name}.ok' criado com sucesso.")

    # em caso de erro...
    except Exception as l_err:
        # log 
        print(f"Erro ao criar o arquivo '{fs_name}.ok'.")
        print(f">> {l_err}. Aborting.")

# -------------------------------------------------------------------------------------
def download(f_rc, fs_fname: str):
    """
    download file
    """
    try:
        # download file
        f_rc.download(fs_fname)
        
    # em caso de erro...
    except Exception as l_err:
        # log
        print(f"Erro no download de {fs_fname}: {l_err}. Aborting...")
        # quit fail
        sys.exit(-1)

    # download ok ?
    if os.path.exists(fs_fname):
        # log
        print("Download concluído com sucesso!")

        # cria arquivo sentinela
        cria_arquivo_ok(fs_fname)

    # senão,...
    else:
        # log
        print("O arquivo não foi encontrado. O download pode ter falhado.")
    
# -------------------------------------------------------------------------------------
def generate(fs_tipo: str, fdct_template: dict):
    """
    gera os dados
    """
    # create client
    l_cli = cdsapi.Client()

    # gera os dados
    l_rc = l_cli.retrieve(fs_tipo, fdct_template)

    # monitora a geração...
    while True:
        # atualiza
        l_rc.update()
        # situação atual
        l_reply = l_rc.reply
        # log
        l_rc.info("Request ID: %s, state: %s" % (l_reply["request_id"], l_reply["state"]))

        # completed ?
        if l_reply["state"] == "completed":
            # ok
            return l_rc

        # queued ou running?
        elif l_reply["state"] in ("queued", "running"):
            # log
            l_rc.info("Request ID: %s, sleep: %s", l_reply["request_id"], DI_WAIT)
            # wait
            time.sleep(DI_WAIT)

        # failed ?
        elif l_reply["state"] in ("failed",):
            # log
            l_rc.error("Message: %s", l_reply["error"].get("message"))
            l_rc.error("Reason:  %s", l_reply["error"].get("reason"))
   
            # for all lines in traceback....
            for ln in l_reply.get("error", {}).get("context", {}).get("traceback", "").split("\n"):
                # empty line ? 
                if ln.strip() == "":
                    # quit 
                    break
                # log
                l_rc.error("  %s", ln)

            # em caso de erro...
            raise Exception("%s. %s." % (l_reply["error"].get("message"), l_reply["error"].get("reason")))
            # quit fail
            return None
            
    # unreachable
    return None

# -------------------------------------------------------------------------------------
def get_pressures(fs_ano: str, fs_mes: str, flst_dias: list):
    """
    get pressure data
    """
    # for all pressures...
    for ls_pressao in DLST_PRESSAO:
        # path
        ls_path = os.path.join(os.path.expanduser("~/reanalise"), fs_ano)
        # filename
        ls_fname = f"{fs_ano}{fs_mes}_pressure_levels_{ls_pressao}.nc"
        # file path
        ls_fpath = os.path.join(ls_path, ls_fname)

        # sentinel already exists ?
        if os.path.exists(ls_fpath + ".ok"):
            # skip this one
            continue

        # build template
        ldct_tmpl = build_template(ls_pressao, fs_ano, fs_mes, flst_dias)

        # append pressure level
        ldct_tmpl["pressure_level"] = ls_pressao

        # generate data
        l_rc = generate("reanalysis-era5-pressure-levels", ldct_tmpl)

        if l_rc:
            # download data
            download(l_rc, ls_fpath)

# -------------------------------------------------------------------------------------
def get_single_levels(fs_ano: str, fs_mes: str, flst_dias: list):
    """
    get single level data
    """
    # path
    ls_path = os.path.join(os.path.expanduser("~/reanalise"), fs_ano)
    # filename
    ls_fname = f"{fs_ano}{fs_mes}_single_levels.nc"
    # file path
    ls_fpath = os.path.join(ls_path, ls_fname)

    # sentinel already exists ?
    if os.path.exists(ls_fpath + ".ok"):
        # skip this one
        return

    # build template
    ldct_tmpl = build_template("single", fs_ano, fs_mes, flst_dias)

    # generate data
    l_rc = generate("reanalysis-era5-single-levels", ldct_tmpl)

    if l_rc:
        # download data
        download(l_rc, os.path.join(ls_path, ls_fname))

# -------------------------------------------------------------------------------------
def main():
    """
    drive app
    """
    # data atual
    ldt_now = datetime.date.today()

    # subtrai um dia do primeiro dia do mes atual
    ldt_prev = ldt_now.replace(day=1) - datetime.timedelta(days=1)

    # ano e o mês para pesquisa
    ls_ano = f"{ldt_prev.year:04d}"
    ls_mes = f"{ldt_prev.month:02d}"

    # lista de strings com os dias do mês atual
    llst_dias = [f"{day:02d}" for day in range(1, ldt_prev.day + 1)]

    # get pressure data
    get_pressures(ls_ano, ls_mes, llst_dias)

    # get single level
    get_single_levels(ls_ano, ls_mes, llst_dias)

# -------------------------------------------------------------------------------------
# bootstrap process
#
if "__main__" == __name__:

    # run app
    main()

# < the end >--------------------------------------------------------------------------
