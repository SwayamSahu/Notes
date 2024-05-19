CREATE TABLE Clients(

ID INT PRIMARY KEY,

   Name VARCHAR(20),

   Email_Id NVARCHAR(20)

);


INSERT INTO Clients VALUES (1, 'George', 'ge.com');

INSERT INTO Clients VALUES (2, 'David', 'da.com');

INSERT INTO Clients VALUES (3, 'Chirs', 'ch.com');

INSERT INTO Clients VALUES (4, 'Morrison', 'mo.com');

INSERT INTO Clients VALUES (5, 'Brian', 'br.com');

SELECT * FROM Clients;


CREATE TABLE Clients_Location(

ID INT PRIMARY KEY,

Country VARCHAR(20),

Country_Code VARCHAR(5)

);

INSERT INTO Clients_Location VALUES (1, 'INDIA', 'IND');

INSERT INTO Clients_Location VALUES (2, 'SPAIN', 'ESP');

INSERT INTO Clients_Location VALUES (3, 'FRANCE', 'FRA');

INSERT INTO Clients_Location VALUES (4, 'ENGLAND', 'ENG');

INSERT INTO Clients_Location VALUES (5, 'POLAND', 'POL');

SELECT * FROM Clients_Location;

--creating View
CREATE VIEW V_Clients

AS

SELECT * FROM Clients;

SELECT * FROM V_Clients;

--create view from multiple tables
CREATE VIEW V_Clients_Loc_All

AS

SELECT Clients.ID, Clients.Name, Clients_Location.Country, Clients_Location.Country_Code

FROM Clients, Clients_Location

WHERE Clients.ID = Clients_Location.ID;

SELECT * FROM V_Clients_Loc_All;


--Inserting data in a view

INSERT INTO V_Clients VALUES (6, 'Aakash', 'update_later');

SELECT * FROM V_Clients;

--Updating a Row in a View in SQL

UPDATE V_Clients SET

Email_Id = 'aa.com'

WHERE ID = 6;

SELECT * FROM V_Clients;

--Deleting a Row in a View

DELETE

FROM V_Clients

WHERE ID = 6;

SELECT * FROM V_Clients;

--Add a new column to view

Alter Table Clients_Location Add City nvarchar(50)
select * from V_Clients_Loc_All
Exec sp_refreshview V_Clients_Loc_All

sp_helptext V_Clients_Loc_All

select * from Clients_Location

--How to Drop a View in SQL

DROP VIEW V_Clients;

SELECT * FROM V_Clients;

--Schema Binding a SQL VIEW

CREATE VIEW DemoView
WITH SCHEMABINDING
AS
     SELECT *
     FROM Clients_Location

	 
	 CREATE VIEW DemoView
WITH SCHEMABINDING
AS
     SELECT ID ,Country, Country_Code
     FROM dbo.Clients_Location;


	 ALTER TABLE Clients_Location ALTER COLUMN Country BIGINT;

--We need to drop the VIEW definition itself along with other dependencies on that table before making a change to the existing table schema.

select * from INFORMATION_SCHEMA.Views

