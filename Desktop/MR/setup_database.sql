-- Movie Recommendation Chatbot Database Setup
-- Run this script in SQL Server Management Studio (SSMS)

-- Create the database
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'MovieChatbot')
BEGIN
    CREATE DATABASE MovieChatbot;
    PRINT '✅ Database "MovieChatbot" created successfully!';
END
ELSE
BEGIN
    PRINT '⚠️ Database "MovieChatbot" already exists.';
END
GO

-- Switch to the new database
USE MovieChatbot;
GO

PRINT '✅ Setup complete! The application will create tables automatically when you run it.';
PRINT '✅ You can now close this window and run the Python application.';
GO
