import csv_diff
import jaydebeapi
import traceback
import configparser
import logging
import os
import re
import click
import subprocess
import pandas as pd
import json
from tabulate import tabulate
import datetime
import os
import sys

user = ''
password = ''
host = ''
database = ''
port = ''
working_directory = os.getcwd()


def db_connect(dbconn):
    try:
        # os.chdir(fpath)
        config = configparser.ConfigParser()
        config.read('C:\\Users\\gomerey02\\Downloads\\CICD_Final\\connect.ini')
        user = config[dbconn]['user']
        password = config[dbconn]['password']
        host = config[dbconn]['host']
        database = config[dbconn]['url']
        port = config[dbconn]['port']
        jars = r'C:\Users\gomerey02\Downloads\Tools\JDBC\postgresql-42.2.22.jar'
        print("config.get('dbconn','jarpath') :" + config[dbconn]['jarpath'])
        conn = jaydebeapi.connect(config[dbconn]['driver'],
                                  config[dbconn]['url'],
                                  {'user': user, 'password': password},
                                  jars)

    except jaydebeapi.DatabaseError as de:
        raise

    try:
        curs = conn.cursor()

    except jaydebeapi.DatabaseError as de:
        raise

    return conn, curs

def get_version(cursor, schema_name, component_name):
    # return the previous version number
    version = 0
    query = "select component_version from " + schema_name + ".component_version where component_name = '" + component_name + "' ORDER BY exce_ts DESC"
    cursor.execute(query)
    version = cursor.fetchone()
    if version == None:
        return 0.0
    else:
        return version[0]


def execute_sqls(source_path, outputpath, cursor, ticketnum):
    conn, cursor = db_connect(dbconn)
    # table_status = checkTableExists(conn,'','component_version')
    # component_version
    # execute scripts from SQL folder and produce .log for each script in OutputFile directory
    command = "psql --host=" + host + " --username=" + user + " --dbname " + database + " --port=" + str(port)
    sql_files = [file for file in os.listdir(source_path) if file.endswith(".sql")]
    cnt = len(sql_files)
    os.chdir(source_path)
    os.chdir('..')
    if not os.path.exists(outputpath):
        os.mkdir(outputpath)
    os.chdir(source_path)
    path1 = os.getcwd()
    parent = os.path.abspath(os.path.join(path1, os.pardir))
    for file in sql_files:
        FileName = file.split('-')
        prev_version = get_version(cursor, FileName[2], FileName[1])
        # print("filename 2 ={} and filename 1 = {}".format(FileName[2],FileName[1]))
        version = (FileName[3][:-4])
        # check if table exists or not
        table_status = checkComponentVersionTableExists(conn, FileName[2], FileName[1])
        if table_status == True:
            print("#####TABLE EXISTED#####")
            print(table_status)
        else:
            createComponentVersionTable(conn, FileName[2], FileName[1])
            print("#####TABLE CREATED#####")
        # print("-----------------------------------------------------------------------------")
        # print("\n Version of {}\n Script Version : {} \n Current Version : {}\n".format(FileName[1],version, prev_version))
        print("\t")
        print(tabulate([["Script", "Current Version", "Script Version", "Schema"],
                        [FileName[1], prev_version, version, FileName[-2]]], headers="firstrow", tablefmt='psql'))

        if float(version) > float(prev_version):
            current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            try:
                print("Applying script {}".format(file))
                command = command + " --file=" + file + " --log-file=" + parent + "\\OutputFile\\" + file[:-4] + ".log"
                os.system(command)
                insertDataInComponentVersionTable(conn, FileName[2], 'component_version', version, FileName[1], file,
                                                  ticketnum, current_timestamp, 'success')
            except:
                insertDataInComponentVersionTable(conn, FileName[2], 'component_version', version, FileName[1], file,
                                                  ticketnum,
                                                  current_timestamp, 'failed')

        else:
            print(
                "Script cannot be applied because the script({}) is older than or equal to the current component version {}.\n".format(
                    version, prev_version))


def dump_to_csv(directory, path_to_scripts, conn):
    # execute sql scripts and generate .csv in OutputFile or GoodFile directories resp. depending on the mode i.e. dump or deploy
    command = "psql --host=" + host + " --username=" + user + " --dbname " + database + " --port=" + str(port)
    sql_files = [file for file in os.listdir(path_to_scripts) if file.endswith(".sql")]
    os.chdir(path_to_scripts)
    path1 = os.getcwd()
    parent = os.path.abspath(os.path.join(path1, os.pardir))
    print(
        "=============================================== Executing SQL ================================================\n")
    for file in sql_files:
        # print("\n==========executing : {}.......==========".format(file))
        # print("\n================== Starting execution for {} ==================".format(file))
        print("\t# Starting execution for {}".format(file))
        f = open(file, 'r')
        DF = pd.read_sql_query(f.read(), conn)
        if directory == 'OutputFile':
            DF.to_csv(parent + "\\OutputFile\\" + file[:-4] + ".csv", index=False, sep="~")
        elif directory == 'GoodFile':
            DF.to_csv(parent + "\\GoodFile\\" + file[:-4] + ".csv", index=False, sep="~")
        print("\t  Execution Completed\n")


def compare_csv(OutFile_path, GoodFile_path):
    # compare .csv files from OutputFile and GoodFile and generate diff.json

    print("\t# Elements of JSON file")
    print(
        "\t1.Added:\n\t\tIf any Columm/Record/Table is added in SQL and it's not in GoodFile\n\t\tthen the difference will be shown in added block of json file.")
    print(
        "\n\t2.Removed:\n\t\tIf any Columm/Record/Table is removed in SQL and it's there in GoodFile\n\t\tthen the difference will be shown in removed block of json file.")
    print(
        "\n\t3.Changed:\n\t\tIf there is any modification in DML statement of SQL query\n\t\tthen the difference will be shown in changed block of json file.")
    print(
        "\n==============================================================================================================\n")

    from csv_diff import load_csv, compare
    import sys
    try:
        os.chdir(OutFile_path)
        output_csvs = [each for each in os.listdir(OutFile_path) if each.endswith('.csv')]
        goodfile_csvs = [each for each in os.listdir(GoodFile_path) if each.endswith('.csv')]
        json_files = [each.split('.')[0] + '.json' for each in output_csvs]
        # print("here is json file",json_files)
        for outfile, goodfile, jsonfile in zip(output_csvs, goodfile_csvs, json_files):
            jsonfile1 = jsonfile
            source = GoodFile_path + "\\" + goodfile
            target = OutFile_path + "\\" + outfile
            jsonfile = OutFile_path + "\\" + jsonfile
            key = "id"
            os.system(
                'csvdiff ' + key + ' --style=pretty --output=' + jsonfile + ' ' + source + ' ' + target + ' --sep="~"')

            # print("{} created successfully.".format(jsonfile))

            try:
                with open(jsonfile) as f:
                    data = json.load(f)
            except EnvironmentError as Error:
                print(Error)

            if (len(data['added']) != 0 or len(data['removed']) != 0 or len(data['changed']) != 0):
                # print("Differences found! please check {} for more details.\n\n".format(jsonfile))
                print("\t# Differences found for {} ".format(jsonfile1[:-4]))
                print("\t  For details of error check {}\n".format(jsonfile1))

            else:
                print("\t# No difference found for {} \n".format(jsonfile1[:-4]))


    except Exception as e:
        logging.error(traceback.format_exc())


def check_logs_for_error(OutFile_path):
    # check logs for error
    log_files = [file for file in os.listdir(OutFile_path) if file.endswith('.log')]
    errors = ['error', 'warning', 'WARNING', 'ERROR', 'Error', 'Warning']
    for file in log_files:
        with open(file) as f:
            for line in f.readlines():
                [print("\t***{} found, please check {} for more details\n".format(error, file)) for error in errors if
                 error in line]
            else:
                print("\t# No Error found in {}.\n".format(file))


@click.command()
@click.option('--mode', default=None, help='Get the mode of execution i.e dump or deploy')
@click.option('--ticketnum', default=None, help='Get the mode of execution i.e dump or deploy')
@click.option('--dbconn', default=None, help='Get the mode of execution i.e dump or deploy')
@click.option('--sqlpath', default=None, help='Get the mode of execution i.e dump or deploy')
@click.option('--outputpath', default=None, help='Get the mode of execution i.e dump or deploy')
def main(mode, ticketnum, dbconn, sqlpath, outputpath):
    conn, cursor = db_connect(dbconn)
    if mode == "dump":
        if not os.path.exists('GoodFile'):
            os.mkdir('GoodFile')
        os.chdir(GoodFile_path)
        dump_to_csv('GoodFile', path_to_scripts, conn)
    elif mode == "deploy":
        if not os.path.exists(outputpath):
            os.mkdir(outputpath)
        execute_sqls(sqlpath, outputpath, cursor, ticketnum)
        # dump_to_csv('OutputFile', path_to_scripts, conn)
        # print("\n===========Comparing files to check difference...==================\n")
        print(
            "\n=============================================== Summary =====================================================\n")
        # compare_csv(OutFile_path, GoodFile_path)
        print(
            "\n=============================================== Logs For Error ==============================================\n")
        check_logs_for_error(outputpath)
    else:
        print("Please enter valid mode i.e.dump or deploy!!")


'''CHECK IF TABLE EXIST OR NOT'''


def checkComponentVersionTableExists(dbcon, schema_name, table_name):
    dbcur = dbcon.cursor()
    dbcur.execute("""
        SELECT COUNT(*)
        FROM {0}.tables
        WHERE table_name = '{1}'
        """.format(schema_name, table_name.replace('\'', '\'\'')))
    if dbcur.fetchone()[0] == 1:
        dbcur.close()
        return True
    dbcur.close()
    return False


'''CREATE A NEW TABLE '''


def createComponentVersionTable(dbcon, schema_name, table_name):
    dbcur = dbcon.cursor()
    dbcur.execute("""
            CREATE TABLE {0}.{1} (
            component_version varchar(100),
			component_name varchar(100),
			script_name varchar(100),
			ticket_desc varchar(100),
			exce_ts timestamp,
			status varchar(10)
			)
            """).format(schema_name, table_name)
    dbcon.commit()
    dbcur.close()


'''INSERT DATA IN COMPONENT VERSION TABLE '''


def insertDataInComponentVersionTable(dbcon, schema_name, table_name, comp_ver, comp_nm, script_nm, tkt_desc, exce_ts,
                                      status):
    dbcur = dbcon.cursor()
    dbcur.execute("""
            INSERT INTO {0}.{1} (
            component_version,
			component_name,
			script_name,
			ticket_desc,
			exce_ts,
			status
			) VALUES ({2},{3},{4},{5},{6})
            """).format(schema_name, table_name, comp_ver, comp_nm, script_nm, tkt_desc, exce_ts, status)
    dbcon.commit()
    dbcur.close()


if __name__ == "__main__":
    main()
