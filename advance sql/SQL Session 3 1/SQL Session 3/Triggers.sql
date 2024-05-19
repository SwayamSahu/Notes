CREATE TRIGGER [schema_name.]trigger_name
ON { table_name | view_name }
{ FOR | AFTER | INSTEAD OF } {[INSERT],[UPDATE],[DELETE]}
[NOT FOR REPLICATION]
AS
    {sql_statements}

--schema_name (optional) is the name of the schema where the new trigger will be created.
--trigger_name is the name of the new trigger.
--ON { table_name | view_name } keyword specifies the table or view name on which the trigger will be created.
--AFTER clause specifies the INSERT, UPDATE or DELETE event which will fire the trigger. The AFTER clause specifies that the trigger fires only after SQL Server successfully completes the execution of the action that fired it. All other actions and constraints should be successfully executed before the trigger is fired.
--INSTEAD OF clause is used to skip an INSERT, UPDATE or DELETE statement to a table and instead, executes other statements defined in the trigger. So, the actual INSERT, UPDATE or DELETE statement does not happen at all. INSTEAD OF clause cannot be used on DDL triggers.	
--INSERTED Table
--DELETED Table

CREATE TABLE Employee
(  
    EmployeeID int NOT NULL,
    FirstName nvarchar(50) NOT NULL,
    LastName nvarchar(50) NOT NULL,
    HireDate date,    
);
CREATE TABLE EmpLog (
   logID INT IDENTITY(1,1) NOT NULL
   , EmployeeID INT NOT NULL
   , FirstName NVARCHAR(50) NOT NULL
   , LastName NVARCHAR(50) NOT NULL
   , HireDate date NOT NULL
   , Operation NVARCHAR(50)
   , UpdatedOn DATETIME
   , UpdatedBy NVARCHAR(50)
   );
GO


--The INSERT Trigger
CREATE TRIGGER trgEmployeeInsert
ON Employee
FOR INSERT
AS
   INSERT INTO EmpLog(EmployeeID, FirstName, LastName, HireDate, Operation, UpdatedOn, UpdatedBy)
   SELECT EmployeeID, Firstname, LastName, HireDate, 'INSERT', GETDATE(), SUSER_NAME()
   FROM INSERTED;
GO

INSERT INTO Employee
VALUES(101, 'Neena','Kochhar','05-12-2018'),
(112, 'John','King','01-01-2015');
GO

SELECT *
FROM EmpLog
ORDER BY EmployeeID;
GO

--The DELETE Trigger

--populating some more data in tbl employee
INSERT INTO Employee
VALUES (203, 'Catherine','Abel','07-21-2010'),
(411, 'Sam','Abolrous','03-12-2016');
GO

CREATE TRIGGER trgEmployeeDelete
ON Employee
FOR DELETE
AS
   INSERT INTO EmpLog(EmployeeID, FirstName, LastName, HireDate, Operation, UpdatedOn, UpdatedBy)
   SELECT EmployeeID, Firstname, LastName, HireDate, 'DELETED', GETDATE(), SUSER_NAME()
   FROM DELETED;
GO

DELETE
FROM Employee
WHERE EmployeeID = 203;
GO

SELECT *
FROM Employee;
GO
SELECT *
FROM EmpLog;
GO

--The UPDATE Trigger

CREATE TRIGGER trgEmployeeUpdate
ON Employee
FOR UPDATE
AS
   INSERT INTO EmpLog(EmployeeID, FirstName, LastName, HireDate, Operation, UpdatedOn, UpdatedBy)
   SELECT EmployeeID, Firstname, LastName, HireDate, 'UPDATE', GETDATE(), SUSER_NAME()
   FROM INSERTED;
GO

UPDATE Employee
SET LastName = 'Adams'
WHERE EmployeeID = 101;
GO

SELECT * FROM Employee;
GO
SELECT * FROM EmpLog;
GO

--Sample trigger to combine INSERT, UPDATE, and DELETE into one trigger.
CREATE TRIGGER trgEmployeeAudit ON dbo.Employee
FOR INSERT, UPDATE, DELETE
AS
IF EXISTS ( SELECT 0 FROM Deleted )
BEGIN
   IF EXISTS ( SELECT 0 FROM Inserted )
   BEGIN
      INSERT  INTO dbo.EmpLog
      ( EmployeeID,
      FirstName,
      LastName,
      HireDate,
      Operation,
      UpdatedOn,
      UpdatedBy
      )
      SELECT  u.EmployeeID ,
      u.FirstName,
      u.LastName ,
      u.HireDate ,
      'Updated',
      GETDATE() ,
      SUSER_NAME()
      FROM deleted as u
   END
ELSE
   BEGIN
      INSERT  INTO dbo.EmpLog
      ( EmployeeID ,
      FirstName,
      LastName,
      HireDate,
      Operation,
      UpdatedOn,
      UpdatedBy
      )
      SELECT  d.EmployeeID ,
      d.FirstName ,
      d.LastName ,
      d.HireDate ,
      'Deleted',
      GETDATE() ,
      SUSER_NAME()
      FROM deleted as d
   END
   END
ELSE
   BEGIN
      INSERT  INTO dbo.EmpLog
      ( EmployeeID ,
      FirstName,
      LastName,
      HireDate,
      Operation,
      UpdatedOn,
      UpdatedBy
      )
      SELECT  i.EmployeeID ,
      i.FirstName ,
      i.LastName ,
      i.HireDate ,
      'Inserted',
      GETDATE() ,
      SUSER_NAME()
      FROM inserted as i
   END   
GO

--The INSTEAD OF Clause
CREATE TABLE HREmployees(
   EmployeeID INT
   , FirstName VARCHAR(20)
   , LastName VARCHAR(20)
   , isActive BIT
   );
GO

INSERT INTO HREmployees(EmployeeID, FirstName, LastName, isActive)
VALUES (111, 'John', 'King', 1)
, (112, 'Sam', 'Smith', 1);
GO

SELECT *
FROM HREmployees;
GO

--Now, let's create a view for the users to access instead of the table itself. In this view, we will not allow them to see the "isActive" column and only allow them to see rows whose "isActive" value is 1.
CREATE VIEW vHREmployees
AS
SELECT 
   EmployeeID
   , FirstName
   , LastName
FROM HREmployees
WHERE isActive = 1;
GO

CREATE TRIGGER trgHREmployeeDoNotDelete
ON HREmployees
INSTEAD OF DELETE
AS
   UPDATE HREmployees
   SET isActive = 0
   WHERE EmployeeID IN (SELECT EmployeeID FROM DELETED)
GO

DELETE
FROM HREmployees
WHERE EmployeeID = 111;
GO

SELECT *
FROM vHREmployees;
GO