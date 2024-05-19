CREATE TABLE Product
(ProductID INT, ProductName VARCHAR(100) )
GO
 
CREATE TABLE ProductDescription
(ProductID INT, ProductDescription VARCHAR(800) )
GO
 
INSERT INTO Product VALUES (680,'HL Road Frame - Black, 58')
,(706,'HL Road Frame - Red, 58')
,(707,'Sport-100 Helmet, Red')
GO
 
INSERT INTO ProductDescription VALUES (680,'Replacement mountain wheel for entry-level rider.')
,(706,'Sturdy alloy features a quick-release hub.')
,(707,'Aerodynamic rims for smooth riding.')
select * from Product
select * from ProductDescription

CREATE PROCEDURE GetProductDesc
AS
BEGIN
SET NOCOUNT ON
 
SELECT P.ProductID,P.ProductName,PD.ProductDescription  FROM 
Product P
INNER JOIN ProductDescription PD ON P.ProductID=PD.ProductID
 
END

EXEC GetProductDesc 

--sp with param

CREATE PROCEDURE GetProductDesc_withparameters
(@PID INT)
AS
BEGIN
SET NOCOUNT ON
 
SELECT P.ProductID,P.ProductName,PD.ProductDescription  FROM 
Product P
INNER JOIN ProductDescription PD ON P.ProductID=PD.ProductID
WHERE P.ProductID=@PID
 
END

EXEC GetProductDesc_withparameters 706


--sp with default
EXEC GetProductDesc_withparameters

CREATE PROCEDURE GetProductDesc_withDefaultparameters
(@PID INT =706)
AS
BEGIN
SET NOCOUNT ON
 
SELECT P.ProductID,P.ProductName,PD.ProductDescription  FROM 
Product P
INNER JOIN ProductDescription PD ON P.ProductID=PD.ProductID
WHERE P.ProductID=@PID
 
END

--output
EXEC GetProductDesc_withDefaultparameters
EXEC GetProductDesc_withDefaultparameters 680

--Creating a stored procedure with an output parameter

CREATE TABLE Employee (EmpID int identity(1,1),EmpName varchar(500))

CREATE PROCEDURE ins_NewEmp_with_outputparamaters
(@Ename varchar(50),
@EId int output)
AS
BEGIN
SET NOCOUNT ON
 
INSERT INTO Employee (EmpName) VALUES (@Ename)
 
SELECT @EId= SCOPE_IDENTITY()
 
END


--output
declare @EmpID INT
 
EXEC ins_NewEmp_with_outputparamaters 'Andrew', @EmpID OUTPUT
 
SELECT @EmpID

declare @EmpID2 INT
 
EXEC ins_NewEmp_with_outputparamaters 'Kate', @EmpID2 OUTPUT
 
SELECT @EmpID2

--creating temp procedures
CREATE PROCEDURE #Temp
AS
BEGIN
PRINT 'Local temp procedure'
END

CREATE PROCEDURE ##TEMP
AS
BEGIN
PRINT 'Global temp procedure'
END


--Modifying the stored procedure
ALTER PROCEDURE GetProductDesc
AS
BEGIN
SET NOCOUNT ON
 
SELECT P.ProductID,P.ProductName,PD.ProductDescription  FROM 
Product P
INNER JOIN ProductDescription PD ON P.ProductID=PD.ProductID
 
END

--Renaming the stored procedure

sp_rename 'GetProductDesc','GetProductDesc_new'