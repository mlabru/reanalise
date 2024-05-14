# -*- coding: utf-8 -*-

# < imports >--------------------------------------------------------------------------

# python library
import datetime
import os
import subprocess
import sys

# -------------------------------------------------------------------------------------
def check_ok(fs_ano: str, fs_mes: str):
    """
    check if the input files are available
    """
    # flag ok
    lv_ok = True

    # for all necessaries files... 
    for ls_fname in (f"{fs_ano}{fs_mes}_single_levels.nc",
                     f"{fs_ano}{fs_mes}_pressure_levels_850.nc",
                     f"{fs_ano}{fs_mes}_pressure_levels_1000.nc"):
        # download ok ?
        lv_ok &= os.path.exists(ls_fname)
        lv_ok &= os.path.exists(ls_fname + ".ok")

    # return
    return lv_ok
        
# -------------------------------------------------------------------------------------
def clean_ok(fs_ano: str, fs_mes: str):
    """
    remove ok files
    """
    # for all files... 
    for ls_fname in (f"{fs_ano}{fs_mes}_single_levels.nc",
                     f"{fs_ano}{fs_mes}_pressure_levels_850.nc",
                     f"{fs_ano}{fs_mes}_pressure_levels_1000.nc"):
        # remove file
        os.remove(ls_fname + ".ok")

# -------------------------------------------------------------------------------------
def run_grads(fs_ano: str, fs_mes: str):
    """
    run GrADS for reanalise
    """
    # open file
    lfh_file = open("../srce/lista.conf", 'r')
    # load file
    llst_lines = lfh_file.readlines()
    # for all lines in file...
    for ls_line in llst_lines:
        # remove <LF>+<CR>
        ls_line = ls_line.rstrip('\n')
        # split args
        ls_station = str(ls_line).split()[-1]

        # build params
        ls_line += f" {fs_ano}{fs_mes}" 
        # build command line
        ls_cmd_exe = f"grads -lbc" + f" 'run ../srce/reanalise_visi.gs {ls_line}' " + \
                     f"> ../srce/logs/{ls_station}.log 2>&1 &"
      
        try:
            # log
            print(f"Executando reanalise de {ls_station}")
            # exec command line
            li_rc = subprocess.call(ls_cmd_exe, shell=True)

        # em caso de erro...
        except subprocess.CalledProcessError as l_err:
            # log erro
            print(f"Erro ao executar reanalise de {ls_station}: {l_err}.")
            # quit fail
            sys.exit(-1)

        # close file
        lfh_file.close()
    
# -------------------------------------------------------------------------------------
def main():
    """
    drive app
    """
    # data atual                                                                        
    ldt_now = datetime.date.today()                                                     
                                                                                        
    # ultimo dia do mes anterior
    ldt_prev = ldt_now.replace(day=1) - datetime.timedelta(days=1)                      
                                                                                        
    # ano e o mês para pesquisa                                                         
    ls_ano = f"{ldt_prev.year:04d}"                                                     
    ls_mes = f"{ldt_prev.month:02d}"                                                    
                                                                                        
    # actual dir
    ls_actual_dir = os.getcwd()
     
    # change to data dir
    os.chdir(os.path.join(os.path.expanduser("~/reanalise"), ls_ano))

    # ano e o mês atual
    if check_ok(ls_ano, ls_mes):
        # run grads
        run_grads(ls_ano, ls_mes)

        # remove sentinel files
        clean_ok(ls_ano, ls_mes)

    # return to actual dir
    os.chdir(ls_actual_dir)

# -------------------------------------------------------------------------------------
if "__main__" == __name__:

    # app
    main()

# < the end >--------------------------------------------------------------------------
