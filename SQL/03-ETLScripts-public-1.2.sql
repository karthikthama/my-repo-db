\echo '*** Insert Sample Data into Employee Table'

INSERT INTO Employee (id, age, first_name, last_name, email)
VALUES(1, 30, 'abc', 'xyz', 'abc.xyz@gmail.com');

INSERT INTO Company (id, name, age, address, salary)
VALUES(1, 'Paul', 32, 'California', 20000), (2, 'Allen', 25, 'Texas', 15000), (3, 'Teddy', 25, 'Norway', 20000), (4, 'Mark', 25, 'Rich-Mond ', 65000), (5, 'David', 27, 'Texas', 85000);

INSERT INTO student(id, name, grade) 
VALUES(100, 'Ram', 'A'), (101, 'Raj', 'C'),(102, 'Radha', 'B'),(103,'Abc','D');
