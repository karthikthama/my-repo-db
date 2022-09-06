import jaydebeapi
#import traceback
import configparser
import os
import click
import subprocess
import pandas as pd
import json
from tabulate import tabulate
import datetime
import sqlparse
import psycopg2
import logging
import sys
import datetime
import os

user=''
password=''
host=''
database=''
port=''
log_file=''
working_directory=os.getcwd()


def db_connect(dbconn):
    try:
    #os.chdir(fpath)
        config = configparser.ConfigParser()
        config.read('/jenkins/python/connect.ini')
        config.read(os.path.join(os.getcwd(), 'connect.ini'))
        global user,password,host,database,port
        user=config[dbconn]['user']
        password=config[dbconn]['password']
        host=config[dbconn]['host']
        database=config[dbconn]['database']
        url=config[dbconn]['url']
        port=config[dbconn]['port']
        jars=r''+ config[dbconn]['jarpath']+''
        #Set Jar in CLASSPATH
        os.environ["CLASSPATH"] = jars

        if dbconn=='DBRDB':
            conn = jaydebeapi.connect(config[dbconn]['driver'],
                                    config[dbconn]['url'])
        else:
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

    return  conn,curs

def create_compt_schema(cursor,schema_name):
    #conn, cursor = db_connect(dbconn)
    try:
        cursor.execute(f"Select 1 from {schema_name}.component_version")
        version = cursor.fetchone()
    except:
        query = f"create table {schema_name}.component_version(component_version varchar(100), component_name varchar(100),script_type varchar(30), tickit_decs varchar(100), exce_ts timestamp, status varchar(100), script_name varchar(100))"
        cursor.execute(query)

def insert_compt_version(cursor,schema_name, comp_version, comp_name,script_type, tic_num, status, filename):
    #conn, cursor = db_connect()
    script_type_desc="NA"
    if script_type=='B':
        script_type_desc='Backup'
    elif script_type=='D':
        script_type_desc='DDL'
    elif script_type=='E':
        script_type_desc='ETL Scripts'
    elif script_type=='F':
        script_type_desc='Static Data'
    elif script_type=='R':
        script_type_desc='Rollback'
    else:
        script_type_desc='NA'
    query = f"INSERT INTO {schema_name}.component_version (component_version, component_name, script_type,tickit_decs, exce_ts, status, script_name) VALUES('{comp_version}', '{comp_name}', '{script_type_desc}', '{tic_num}', current_timestamp, '{status}', '{filename}');"
    cursor.execute(query)


def get_version(cursor, schema_name, component_name,script_type_desc):
    #return the previous version number
    version = 0
    query = f"select component_version from { schema_name }.component_version where status='Success'and script_type ='{script_type_desc}' and component_name = '{component_name}' order by exce_ts desc,component_version desc"
    cursor.execute(query)
    version = cursor.fetchone()
    if version==None:
        return 0.0
    else:
        return version[0]


def execute_sqls(dbconn,source_path,tic_num,rollback,logmode,logpath):
    try:
        logger = logging.getLogger('')
        if logmode=="DEBUG":
            logger.setLevel(logging.DEBUG)
        elif logmode=="WARNING":
            logger.setLevel(logging.WARNING)
        elif logmode=="ERROR":
            logger.setLevel(logging.ERROR)
        else:
            logger.setLevel(logging.INFO)
        global log_file
        log_file = datetime.datetime.now().strftime(tic_num+'_%H_%M_%d_%m_%Y.log')
        fh = logging.FileHandler(f'{logpath}{log_file}')
        sh = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('[%(asctime)s] - %(levelname)s - %(message)s',datefmt='%a, %d %b %Y %H:%M:%S')
        fh.setFormatter(formatter)
        sh.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(sh)
        #execute scripts from SQL folder and produce .log for each script in OutputFile directory
        sql_files = [file for file in os.listdir(source_path) if file.endswith(".sql")]
        cnt = len(sql_files)
        os.chdir(source_path)
        logging.info("==================== Connecting to Database ======================")
        logging.info("    Connection Name     " +  dbconn)
        logging.info("==================================================================")
        conn,cursor = db_connect(dbconn)

        for file in sql_files:
            try:
                FileName = file.split('-')
                component_version=FileName[0]
                component_name=FileName[2]
                script_type=FileName[1]
                schema_name=FileName[3][:-4]
                tickit_decs=tic_num
                script_name=file
                script_type_desc="NA"
                # Script Type
                if script_type=='B':
                    script_type_desc='Backup'
                elif script_type=='D':
                    script_type_desc='DDL'
                elif script_type=='E':
                    script_type_desc='ETL Scripts'
                elif script_type=='F':
                    script_type_desc='Static Data'
                elif script_type=='R':
                    script_type_desc='Rollback'
                else:
                    script_type_desc='NA'
                create_compt_schema(cursor,schema_name)
                prev_version = get_version(cursor, schema_name, component_name,script_type_desc)

                try:
                    if ((rollback == "Y") and (script_type=='R')):
                        if float(component_version) > float(prev_version):
                            logging.info("\t")
                            logging.info("---------------------------------------------------------------------------------------")
                            logging.info(" Processing Script : " +file)
                            logging.info("---------------------------------------------------------------------------------------")
                            logging.info(f"     Component : {component_name}")
                            logging.info(f"     Database Current Version : {prev_version}")
                            logging.info(f"     Script Version : {component_version}")
                            logging.info(f"     Schema :  { schema_name}")
                            logging.info(f"     Ticket No : {tic_num}")
                            logging.info("---------------------------------------------------------------------------------------")
                            fd = open(file, 'r')
                            sqlFile = fd.read()
                            fd.close()
                            statementlist= sqlparse.split(sqlFile)
                            for index,statement in enumerate(statementlist):
                                logging.info(f" Executing Statement : {index+1}")
                                logging.debug(sqlparse.format(statement, reindent=True, keyword_case='upper'))
                                cursor.execute(sqlparse.format(statement, reindent=True, keyword_case='upper'))
                                logging.info("........Done !")
                            insert_compt_version(cursor,schema_name, component_version, component_name,script_type, tickit_decs, 'Success', script_name)
                        else:
                            logging.warning(f"{file} Script cannot be applied! The script is older version or has already been deployed to database earlier")
                    elif ((rollback == 'N') and (script_type!='R')):
                        if float(component_version) > float(prev_version):
                            logging.info("\t")
                            logging.info("---------------------------------------------------------------------------------------")
                            logging.info(" Processing Script : " +file)
                            logging.info("---------------------------------------------------------------------------------------")
                            logging.info(f"     Component : {component_name}")
                            logging.info(f"     Database Current Version : {prev_version}")
                            logging.info(f"     Script Version : {component_version}")
                            logging.info(f"     Schema :  { schema_name}")
                            logging.info(f"     Ticket No : {tic_num}")
                            logging.info("---------------------------------------------------------------------------------------")
                            fd = open(file, 'r')
                            sqlFile = fd.read()
                            fd.close()
                            statementlist= sqlparse.split(sqlFile)
                            for index,statement in enumerate(statementlist):
                                logging.info(f" Executing Statement : {index+1}")
                                logging.debug(sqlparse.format(statement, reindent=True, keyword_case='upper'))
                                cursor.execute(sqlparse.format(statement, reindent=True, keyword_case='upper'))
                                logging.info("........Done !")
                            insert_compt_version(cursor,schema_name, component_version, component_name,script_type, tickit_decs, 'Success', script_name)
                        else:
                            logging.warning(f"{file} Script cannot be applied! The script is older version or has already been deployed to database earlier")
                except Exception as e:
                    logging.error(".........Failed !")
                    insert_compt_version(cursor,schema_name, component_version, component_name,script_type, tickit_decs, 'Failed', script_name)
                    logging.error(e)
                    logging.error("***  Deployment aborted because of Errors, Please fix the issue before proceeding !  ***")
                    break
                    sys.exit(-1)


            except Exception as e:
                logging.error(e)

        conn.close()
    except Exception as e:
        logging.error(e)


def check_logs_for_error(logpath):
    # check logs for error
    os.chdir(logpath)
    print(f'{logpath}{log_file}')
    print("--------------------------------------------------------------------------------------")
    errors = ['error', 'ERROR', 'Error', 'Failed']
    with open(f'{logpath}{log_file}') as f:
        for line in f.readlines():
            for error in errors:
                if error in line:
                    sys.exit(f"Errors found! Please check the log file {log_file} for more details ")
        else:
            print("\t# No Error found in {}.\n".format(f'{logpath}{log_file}'))
    print("======================================================================================")

@click.command()
@click.option('--dbconn', default= None, help = 'db connection')
@click.option('--sqlpath', default= None, help = 'Path of SQL files for the execution')
@click.option('--ticket', default= None, help = 'Service ticket no.')
@click.option('--rollback', default="N", help = 'Apply rollback Y OR N')
@click.option('--logmode', default="INFO", help = 'Logging mode INFO, DEBUG, WARNING or ERROR')
@click.option('--logpath', default=None, help = 'Location of the log file')
def main(dbconn,sqlpath,ticket,rollback,logmode,logpath):
    print(rollback)
    os.chdir(sqlpath)
    if not os.path.exists(logpath):
        os.mkdir(logpath)

    execute_sqls(dbconn,sqlpath,ticket,rollback,logmode,logpath)
    check_logs_for_error(logpath)

if __name__ == "__main__":
    main()


# python execute_v2.py   --dbconn=PGDB --sqlpath=C:\\Users\\gomerey02\\Downloads\\CICD_Final\\New  --ticket=BH122345 --logpath=C:\\Users\\gomerey02\\Downloads\\CICD_Final
#Last updated on 25August2022 12:33PM
#Execution command: python3.6 /jenkins/python/execute_new.py --dbconn=PGDB --sqlpath=/jenkins/python/sql --ticket=BH-1234 --logpath=/jenkins/python/logs
