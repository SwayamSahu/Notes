CREATE DATABASE [sample] 
    ON (NAME = N'sample', FILENAME = N'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\sample.mdf', SIZE = 1024MB, FILEGROWTH = 256MB)
LOG ON (NAME = N'sample_log', FILENAME = N'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\sample_log.ldf', SIZE = 512MB, FILEGROWTH = 125MB)
GO
 
-- change owner to sa
ALTER AUTHORIZATION ON DATABASE::[sample] TO [sa]
GO
 
-- set recovery model to simple 
ALTER DATABASE [sample] SET RECOVERY SIMPLE 
GO
 
-- change compatibility level
ALTER DATABASE [sample] SET COMPATIBILITY_LEVEL = 110
GO