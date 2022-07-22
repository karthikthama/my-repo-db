CREATE TABLE backup.bkp_tbls_1st.22-july-2022_public_Persons as select * FROM public.Persons;

INSERT INTO Persons (PersonID, LastName, FirstName, Address, City) VALUES
(007, 'ms', 'dhoni', 'india', 'ranchi'),
(777, 'chris', 'gayle', 'westindies', 'dwain');
