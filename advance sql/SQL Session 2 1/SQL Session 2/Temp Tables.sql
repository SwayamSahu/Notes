--Local Temp table

CREATE TABLE #EmpDetails (id INT, name VARCHAR(25)) 
INSERT INTO #EmpDetails VALUES (01, 'Lalit'), (02, 'Atharva') 

select name from tempdb..sysobjects where name like '#EmpDetails%'


--Global Temp table
CREATE TABLE ##EmpDetails (id INT, name VARCHAR(25)) 
INSERT INTO ##EmpDetails VALUES (01, 'Lalit'), (02, 'Atharva') 

select name from tempdb..sysobjects where name like '##EmpDetails%'