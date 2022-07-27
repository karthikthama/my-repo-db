CREATE TABLE PlayerHistory(
    BusinessEntityID INT NOT NULL,
    RateChangeDate TIMESTAMP NOT NULL,
    Rate numeric NOT NULL, -- money
    PayFrequency smallint NOT NULL,  -- tinyint
    ModifiedDate TIMESTAMP NOT NULL CONSTRAINT "DF_EmployeePayHistory_ModifiedDate" DEFAULT (NOW()),
    CONSTRAINT "CK_EmployeePayHistory_PayFrequency" CHECK (PayFrequency IN (1, 2)), -- 1 = monthly salary, 2 = biweekly salary
    CONSTRAINT "CK_EmployeePayHistory_Rate" CHECK (Rate BETWEEN 6.50 AND 200.00)
  )
