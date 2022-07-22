 CREATE TABLE EmployeeDepartmentHistory(
    BusinessEntityID INT NOT NULL,
    DepartmentID smallint NOT NULL,
    ShiftID smallint NOT NULL, -- tinyint
    StartDate DATE NOT NULL,
    EndDate DATE NULL,
    ModifiedDate TIMESTAMP NOT NULL CONSTRAINT "DF_EmployeeDepartmentHistory_ModifiedDate" DEFAULT (NOW()),
    CONSTRAINT "CK_EmployeeDepartmentHistory_EndDate" CHECK ((EndDate >= StartDate) OR (EndDate IS NULL))
  )

