CREATE TABLE Person
(
    Id INT PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50)
)


--Auto Commit Mode of Transactions
-- --Implicit Transaction Mode in SQL Server:
SET IMPLICIT_TRANSACTIONS ON

INSERT INTO Person VALUES (1, 'Nadim', 'Attar');
INSERT INTO Person VALUES (2, 'Belal', 'Attar');

COMMIT TRANSACTION

INSERT INTO Person VALUES (3, 'Hossam', 'Ekko');
UPDATE Person SET LastName = 'Ekko' WHERE Id = 2;
ROLLBACK TRANSACTION;

select * from Person
--drop table Person

SET IMPLICIT_TRANSACTIONS OFF

--Explicit Transaction Mode in SQL Server:

CREATE PROCEDURE SPAddPerson
AS
BEGIN
   BEGIN TRANSACTION
      INSERT INTO Person VALUES(5, 'Hossami', 'Ekko')
      INSERT INTO Person VALUES(6, 'Mothannam', 'Al Assar')
	  
      IF(@@ERROR > 0)
      BEGIN
         ROLLBACK TRANSACTION
      END
      ELSE
      BEGIN
         COMMIT TRANSACTION
      END  

end

exec SPAddPerson
