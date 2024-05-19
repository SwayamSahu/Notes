--Handling errors using TRY…CATCH

BEGIN TRY  
     --code to try 
END TRY  
BEGIN CATCH  
     --code to run if an error occurs
--is generated in try
END CATCH

ERROR_NUMBER – Returns the internal number of the error
ERROR_STATE – Returns the information about the source
ERROR_SEVERITY – Returns the information about anything from informational errors to errors user of DBA can fix, etc.
ERROR_LINE – Returns the line number at which an error happened on
ERROR_PROCEDURE – Returns the name of the stored procedure or function
ERROR_MESSAGE – Returns the most essential information and that is the message text of the error

USE Sample
GO
-- Basic example of TRY...CATCH
 
BEGIN TRY
-- Generate a divide-by-zero error  
  SELECT
    1 / 0 AS Error;
END TRY
BEGIN CATCH
  SELECT
    ERROR_NUMBER() AS ErrorNumber,
    ERROR_STATE() AS ErrorState,
    ERROR_SEVERITY() AS ErrorSeverity,
    ERROR_PROCEDURE() AS ErrorProcedure,
    ERROR_LINE() AS ErrorLine,
    ERROR_MESSAGE() AS ErrorMessage;
END CATCH;
GO

--Using TRY CATCH with transactions example


CREATE TABLE dbo.persons
(
    person_id  INT
    PRIMARY KEY IDENTITY, 
    first_name NVARCHAR(100) NOT NULL, 
    last_name  NVARCHAR(100) NOT NULL
);

CREATE TABLE dbo.deals
(
    deal_id   INT
    PRIMARY KEY IDENTITY, 
    person_id INT NOT NULL, 
    deal_note NVARCHAR(100), 
    FOREIGN KEY(person_id) REFERENCES dbo.persons(
    person_id)
);


insert into 
    dbo.persons(first_name, last_name)
values
    ('John','Doe'),
    ('Jane','Doe');

insert into 
    dbo.deals(person_id, deal_note)
values
    (1,'Deal for John Doe');
	go

	select * from dbo.persons
	select * from dbo.deals

--create procedure
	CREATE PROC usp_report_error
AS Begin
    SELECT   
        ERROR_NUMBER() AS ErrorNumber  
        ,ERROR_SEVERITY() AS ErrorSeverity  
        ,ERROR_STATE() AS ErrorState  
        ,ERROR_LINE () AS ErrorLine  
        ,ERROR_PROCEDURE() AS ErrorProcedure  
        ,ERROR_MESSAGE() AS ErrorMessage;  
		END
GO

--Then, develop a new stored procedure that deletes a row from the dbo.persons table:

CREATE PROC usp_delete_person(
    @person_id INT
) AS
BEGIN
    BEGIN TRY
        BEGIN TRANSACTION;
        -- delete the person
        DELETE FROM dbo.persons 
        WHERE person_id = @person_id;
        -- if DELETE succeeds, commit the transaction
        COMMIT TRANSACTION;  
    END TRY
    BEGIN CATCH
        -- report exception
        EXEC usp_report_error;
        
        -- Test if the transaction is uncommittable.  
        IF (XACT_STATE()) = -1  
        BEGIN  
            PRINT  N'The transaction is in an uncommittable state.' +  
                    'Rolling back transaction.'  
            ROLLBACK TRANSACTION;  
        END;  
        
        -- Test if the transaction is committable.  
        IF (XACT_STATE()) = 1  
        BEGIN  
            PRINT N'The transaction is committable.' +  
                'Committing transaction.'  
            COMMIT TRANSACTION;     
        END;  
    END CATCH
END;
GO

--XACT_STATE() function to check the state of the transaction before performing COMMIT TRANSACTION or ROLLBACK TRANSACTION inside the CATCH block.
--After that, call the usp_delete_person stored procedure to delete the person id 2:


select * from persons
select * from deals
EXEC usp_delete_person 2;--no exception

EXEC usp_delete_person 1;--execption

exec usp_report_error


