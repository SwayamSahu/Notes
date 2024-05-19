--IF ELSE Statement in SQL Server

IF Boolean_expression   
     { sql_statement | statement_block }   
[ ELSE   
     { sql_statement | statement_block } ]

	 
	 DECLARE @mySalary INT = 5000,
	 @avgSalary INT = 4000;

IF @mySalary > @avgSalary
	PRINT 'My Salary is above the average salary.';
ELSE
	PRINT 'My Salary is less than the average salary.';
--------------------------------------------------------------
if (select AVG(Salary) from Employee)  > 5000
	print 'Average salary is greater than 5000';
else
	print 'Average salary is less than 5000';
--------------------------------------------------------------
--Nested If Else

DECLARE @StudentMarks INT = 85;

IF (@StudentMarks > 80)
	BEGIN
		IF @StudentMarks > 90
			PRINT 'A+';
		ELSE
			PRINT 'A-';
	END	
ELSE 
	PRINT 'Below A grade'