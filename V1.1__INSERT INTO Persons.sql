CREATE TABLE backup.bkp_tbls_1st_22_july_2022_public_Persons as select * FROM public.Persons;

INSERT INTO Persons (PersonID, LastName, FirstName, Address, City) VALUES
(007, 'ms', 'dhoni', 'india', 'ranchi'),
(777, 'chris', 'gayle', 'westindies', 'dwain');
