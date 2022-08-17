\echo '*** Drop and Recreate Student Table'

drop table student;
CREATE TABLE student(id  INT, name varchar(50), grade char);

\echo '*** Drop and Recreate emp_view '
drop view emp_view;
drop table Employee;
CREATE TABLE Employee (
id INT ,
age INT,
first_name VARCHAR(255),
last_name VARCHAR(255),
email varchar(500)
);

\echo '*** Drop and Recreate Company '
drop view COMPANY_VIEW;
drop table Company;
CREATE TABLE Company (
id INT ,
name VARCHAR(255),
age INT,
address VARCHAR(255),
salary INT
);	

\echo '*** Drop and Recreate emp_view '
CREATE VIEW emp_view AS
SELECT first_name, last_name
FROM Employee;
--WHERE (id == 1);


\echo '*** Drop and Recreate Function COMPANY_VIEW '
CREATE VIEW COMPANY_VIEW AS
SELECT ID, NAME, AGE
FROM  COMPANY;

\echo '*** Drop and Recreate emp_view '
CREATE OR REPLACE FUNCTION totalRecords ()
RETURNS integer AS $total$
declare
	total integer;
BEGIN
   SELECT count(*) into total FROM COMPANY;
   RETURN total;
END;
$total$ LANGUAGE plpgsql;

\echo '*** Drop and Recreate Function get_film_count '
CREATE OR REPLACE FUNCTION get_film_count(len_from int, len_to int)
returns int
language plpgsql
as
$$
declare
   film_count integer;
begin
   select count(1) 
   into film_count
   from film
   where length between len_from and len_to;
   
   return film_count;
end;
$$;

\echo '*** Drop and Recreate Function lo_size '
CREATE OR REPLACE FUNCTION lo_size(oid) RETURNS bigint
AS $$
DECLARE
 fd integer;
 sz bigint;
BEGIN
 fd := lo_open($1, 262144); -- INV_READ
 if (fd < 0) then
   raise exception 'Failed to open large object %', $1;
 end if;
 sz := lo_lseek64(fd, 0, 2);
 if (lo_close(fd) <> 0) then
   raise exception 'Failed to close large object %', $1;
 end if;
 return sz;
END;
$$ LANGUAGE plpgsql VOLATILE;


\echo '*** Drop and Recreate Function global_regexp_search '
CREATE OR REPLACE FUNCTION global_regexp_search(
    search_re text,
    param_tables text[] default '{}',
    param_schemas text[] default '{public}',
    progress text default null -- 'tables','hits','all'
)
RETURNS table(schemaname text, tablename text, columnname text, columnvalue text, rowctid tid)
AS $$
declare
  query text;
begin
  FOR schemaname,tablename IN
      SELECT t.table_schema, t.table_name
      FROM   information_schema.tables t
	JOIN information_schema.table_privileges p ON
	  (t.table_name=p.table_name AND t.table_schema=p.table_schema
	      AND p.privilege_type='SELECT')
	JOIN information_schema.schemata s ON
	  (s.schema_name=t.table_schema)
      WHERE (t.table_name=ANY(param_tables) OR param_tables='{}')
        AND t.table_schema=ANY(param_schemas)
        AND t.table_type='BASE TABLE'
  LOOP
    IF (progress in ('tables','all')) THEN
      raise info '%', format('Searching globally in table: %I.%I',
         schemaname, tablename);
    END IF;

    query := format('SELECT ctid FROM %I.%I AS t WHERE cast(t.* as text) ~ %L',
	    schemaname,
	    tablename,
	    search_re);
    FOR rowctid IN EXECUTE query
    LOOP
      FOR columnname IN
	  SELECT column_name
	  FROM information_schema.columns
	  WHERE table_name=tablename
	    AND table_schema=schemaname
      LOOP
	query := format('SELECT %I FROM %I.%I WHERE cast(%I as text) ~ %L AND ctid=%L',
	  columnname, schemaname, tablename, columnname, search_re, rowctid);
        EXECUTE query INTO columnvalue;
	IF columnvalue IS NOT NULL THEN
	  IF (progress in ('hits', 'all')) THEN
	    raise info '%', format('Found in %I.%I.%I at ctid %s, value: ''%s''',
		   schemaname, tablename, columnname, rowctid, columnvalue);
	  END IF;
	  RETURN NEXT;
	END IF;
      END LOOP; -- for columnname
    END LOOP; -- for rowctid
  END LOOP; -- for table
END;
$$ language plpgsql;

\echo '*** Drop and Recreate Function fun1 '
Create or replace function fun1(n int) returns int 
as
$$
Begin
Insert into test values (n,'2019-11-26');
Return 1;
End;
$$
Language 'plpgsql';

