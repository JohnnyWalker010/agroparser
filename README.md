# Agroparser Django Project

This README provides an overview of the project's functionality, setup instructions, and usage guidelines.

## Introduction

Agroparser is a Django-based web application designed to facilitate data scraping and user management. It features JWT-based authentication, user registration, and a web scraper for extracting product data from predefined URLs.

## Installation

### 1. Clone the repository:

`git clone https://github.com/JohnnyWalker010/agroparser.git`

`cd agroparser`

### 2. Create and activate a virtual environment:

`python -m venv venv`

On macOS: `source venv/bin/activate`

On Windows: `venv\Scripts\activate`

### 3. Install dependencies:

`pip install -r requirements.txt`


### 4. Create a superuser or use credentials of an existing one:

`python manage.py createsuperuser`

or 

login: superuser

password: superuser1

### 5. Run the development server:

`python manage.py runserver`
