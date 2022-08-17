import jaydebeapi
import traceback
import configparser
import os
import click
import subprocess
import pandas as pd
import json
from tabulate import tabulate
import datetime

user=''
password=''
host=''
database=''
port=''
working_directory=os.getcwd()

def db_connect(dbconn):
    try:
    #os.chdir(fpath)        
        config = configparser.ConfigParser()
        print ("==================== Connecting to Database ======================")
        config.read('C:\\Users\\gomerey02\\Downloads\\CICD_Final\\connect.ini')
        config.read(os.path.join(os.getcwd(), 'connect.ini')) 
        global user,password,host,database,port
        user=config[dbconn]['user']
        password=config[dbconn]['password']
        host=config[dbconn]['host']
        database=config[dbconn]['database']
        url=config[dbconn]['url']
        port=config[dbconn]['port']
        print ("    Connection Name     " +  dbconn)        
        print ("==================================================================")        
        jars=r''+ config[dbconn]['jarpath']+''
        conn = jaydebeapi.connect(config[dbconn]['driver'],
                                config[dbconn]['url'],
                                {'user': user, 'password':password},                         
                                jars)
        
    except jaydebeapi.DatabaseError as de:
        raise

    try:
        curs = conn.cursor()
        
    except jaydebeapi.DatabaseError as de:
        raise
        
    return conn, curs
    
def create_compt_schema(cursor,schema_name):
    #conn, cursor = db_connect(dbconn)
    query = f"create table if not exists {schema_name}.component_version(component_version varchar(100), component_name varchar(100), tickit_decs varchar(100), exce_ts timestamp, status varchar(100), script_name varchar(100))"
    cursor.execute(query)

def insert_compt_version(cursor,schema_name, comp_version, comp_name, tic_num, status, filename):
    #conn, cursor = db_connect()
    query = f"INSERT INTO {schema_name}.component_version (component_version, component_name, tickit_decs, exce_ts, status, script_name) VALUES('{comp_version}', '{comp_name}', '{tic_num}', current_timestamp, '{status}', '{filename}');"
    cursor.execute(query)
    
    
def get_version(cursor, schema_name, component_name):
    #return the previous version number
    version = 0
    query = "select component_version from " + schema_name + ".component_version where component_name = '" + component_name + "' order by exce_ts desc"
    cursor.execute(query)  
    version = cursor.fetchone()
    if version==None:
        return 0.0
    else:
        return version[0]
    

def execute_sqls(source_path,cursor, tic_num):
    try:
        #execute scripts from SQL folder and produce .log for each script in OutputFile directory
        command = "psql --host=" + host + " --username=" + user + " --dbname " + database + " --port=" + str(port)        
        sql_files = [file for file in os.listdir(source_path) if file.endswith(".sql")]
        cnt = len(sql_files)
        os.chdir(source_path)

        for file in sql_files:
            try:
                FileName = file.split('-')
                create_compt_schema(cursor,FileName[2])
                prev_version = get_version(cursor, FileName[2], FileName[1])                
                version =  FileName[3][:-4]
                print("-----------------------------------------------------------------------------")
                print("\t")
                print(tabulate([["Script","Database Current Version","Script Version","Schema"],[FileName[1], prev_version,version,FileName[-2]]] ,headers="firstrow",tablefmt='psql'))
                        
                if float(version) > float(prev_version):
                    try:
                        print("          Applying script {}".format(file)              )
                        print("-----------------------------------------------------------------------------")
                        command = command + " --file=" + file + " --log-file="+ tic_num +"\\" + file[:-4] + ".log" 
                        os.system(command)
                        insert_compt_version(cursor,FileName[2], (FileName[3][:-4]), FileName[1], tic_num, 'Success', file)
                    except:
                        insert_compt_version(cursor,FileName[2], (FileName[3][:-4]), FileName[1], tic_num, 'Failed', file)
                else:
                    print("Script cannot be applied because the script({}) is older than or equal to the current component version {}.\n".format(version,prev_version))
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

def check_logs_for_error(sqlpath,OutFile_path):
    #check logs for error
    os.chdir(sqlpath + "/" + OutFile_path)   
    print("-- Path of Log Files: " + os.getcwd())
    log_files = [file for file in os.listdir(os.chdir(sqlpath + "/" + OutFile_path)) if file.endswith('.log')]
    print("-- Log files list : ")
    print(log_files)
    print("--------------------------------------------------------------------------------------")       
    errors = ['error', 'warning', 'WARNING', 'ERROR', 'Error', 'Warning']
    for file in log_files:
        with open(file) as f:
            for line in f.readlines():
                [print("\t***{} found, please check {} for more details\n".format(error, file)) for error in errors if error in line]
            else:
                print("\t# No Error found in {}.\n".format(file))
    print("======================================================================================")  

@click.command()
@click.option('--dbconn', default= None, help = 'db connection')
@click.option('--sqlpath', default= None, help = 'Path of SQL files for the execution')
@click.option('--ticket', default= None, help = 'Service ticket no.')
def main(dbconn,sqlpath,ticket): 
    conn, cursor = db_connect(dbconn)
    os.chdir(sqlpath)
    if not os.path.exists(ticket):
        os.mkdir(ticket)
           
    execute_sqls(sqlpath,cursor, ticket)
    print("\n================= Checking Log Files for Errors & Warnings ======================\n")
    check_logs_for_error(sqlpath,ticket)

if __name__ == "__main__":
    main()


# python execute_sql.py   --dbconn=PGDB --sqlpath=C:\\Users\\gomerey02\\Downloads\\CICD_Final\\SQL --ticket=BH122345