# ImageVault

A FastAPI-based image storage API with JWT authentication and user-owned image management.

## Features

* User Registration & Login
* JWT Authentication
* Refresh Tokens
* Protected Routes
* Image Upload
* View User Images
* Delete User Images
* Middleware Logging
* Rate Limiting
* Global Exception Handling

## Tech Stack

* FastAPI
* SQLModel
* SQLite
* JWT
* Passlib (bcrypt)

## Setup

```bash
git clone <repo-url>
cd ImageVault

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

## Configuration

This project requires environment variables to run.

Create your own local configuration file and provide the required values. Do not commit secrets to source control.

## Run

```bash
uvicorn main:app --reload
```

## API Endpoints

### Authentication

* POST /register
* POST /login
* POST /refresh

### Images

* POST /upload
* GET /my-images
* DELETE /images/{image_id}

## Concepts Implemented

* Authentication & Authorization
* JWT Access Tokens
* Refresh Tokens
* Dependency Injection
* Middleware
* Exception Handling
* File Upload Management
* Database CRUD Operations
* User Resource Ownership Validation

```
```
