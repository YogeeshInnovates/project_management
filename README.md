Task Management System (FastAPI)

A simple Task Management API built with FastAPI, SQLAlchemy, and JWT-based authentication. The system allows users to register, login, create tasks, view tasks, update tasks, update task status, and delete tasks. It supports role-based access (admin and user).

Table of Contents

Features

Technologies Used

Setup & Installation

Database Schema

API Endpoints

Authentication

Role-based Access

Usage Example

Features

User registration with role selection (admin/user)

Secure password hashing using bcrypt

JWT-based authentication for login sessions

Admin can create, update, delete, and view all tasks

Users can view tasks assigned to them or tasks they created

Update task status (pending, in-progress, completed)

View tasks filtered by status

Logout functionality

Technologies Used

Python 3.11+

FastAPI

SQLAlchemy

SQLite/MySQL (any SQL database)

Setup & Installation

Clone the repository:

git clone https://github.com/YogeeshInnovates/project_management
cd project_management


Start the FastAPI server:

uvicorn main:app --reload


Database Models
User Table (register)
Column	Type	Description
id	Integer	Primary key
username	String	Unique username
email	String	Unique email
password	String	Hashed password (bcrypt)
role	String	admin or user
Task Table (taskassign)
Column	Type	Description
id	Integer	Primary key
title	String	Task title
description	String	Task description
status	String	Task status (pending, in-progress, completed)
created_at	DateTime	Task creation timestamp (default now)
created_by	Integer	Foreign key to register.id (creator)
assigned_to	Integer	Foreign key to register.id (assignee)

Relationships:

creater → links task to the user who created it (created_by)

assignee → links task to the user assigned to it (assigned_to)

Passlib (for password hashing)

PyJWT (for token-based authentication)
