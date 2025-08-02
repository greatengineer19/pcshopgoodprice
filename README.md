# PCSHOPGOODPRICE
## BUYER AND SELLER PLATFORM, AN ONLINE COMPUTER SHOP

&nbsp;
&nbsp;
&nbsp;
&nbsp;

[www.pcshopgoodprice.com](https://www.pcshopgoodprice.com) is a fullstack portfolio made by **Juan Andrew** between March - August 2025, as a side project after working hours.

## AWS Architecture Diagram
*available soon*

## Tech stacks
My tech stacks evolves to meet the needs of the product features, and the current tools are:
### Backend Stacks
1. FastAPI
2. Python
3. Pytest (Testing framework)
4. SQL Alchemy (Database toolkit)
5. Pydantic (API Schema tools)
6. Apscheduler (Job scheduling tools for FastAPI)
7. PostgreSQL v17.5
### Frontend Stacks
1. NextJS (v15.x)
2. React (v19.x)
3. Typescript v5
4. Tailwind CSS
5. Shadcn UI (Internet-provided UI components library)
6. Radix UI (Internet-provided UI components library)
7. Sonner (Library for displaying toast notifications)
### Frontend Cloud Platform
1. Vercel
### Infrastructures
1. Amazon E. Load Balancer
2. Amazon Route53
3. Amazon EC2
4. Amazon RDS
5. Amazon S3 Bucket
6. Docker
7. Nginx (Web server or reverse proxy)

## Pytest (Tested them all!)
Currently my pytest already tests all API calls, from normal CRUD operations, background tasks, decoupled services, and functions such as authorization.

## Project Structure
This repository is meant for the backend fastapi codes, with the project structures as follow:
- src
    - api
        - api (includes various routers, initialized recurring background tasks, and CORS configuration) 
        - routers (a routes or files that consists of the codes of the API entry code, or business logics)
        - dependencies (Dependency or reusable functions accross different files) 
    - database (engine initialization based on environment of staging, test, or production)
    - models (SQLAlchemy models configuration)
    - schemas (Pydantic schemas parameters and responses and validations)
    - computer_components
        - service (A reusable service for table or route of ComputerComponent)
- tests
    - factories (FactoryBoy for generating a new instance record)
    - conftest (Configuration file before and after tests)
- utils
    - auth (Authentication using JWT OAuth2)
    - password (Password security and verification using BCrypt)


In this
Hassle Free Computers Shop and Admin is a e-commerce website of a single seller brand, with capability of procuring computer components, track inventories history, and shopping and checkouts features.
Initially named Hassle Free Computers Shop and Admin, the name is adjusted to PC Shop Good Price for more readability and easy to memorize.

Summary of technical features are as listed:
1. System design in one JPG
2. All tech stacks:
    - Frontend: Next.JS
    - Deployment UI: Vercel
    - Backend: FastApi Python, PyTest, PostgreSQL
      - PyTest covered all API call, background tasks, and reusable functions such as Authorization
      - Structured projects by folder and service, according to the model_name. E.G sales_invoices project will have directory such as src/api/sales_invoices.py (for routing), and src/sales_invoices (folder specific for model services)
    - Deployment Server: AWS EC2, AWS RDS
    - Infrastructure: Docker

Timeline of finishing the project:
1. 1st March 2025, I began to learn about Python FastApi, Next.JS, and Docker for this self-project. The idea of building the e-commerce project was because I need to learn new stacks of programming language, and the project must be able to be used by all those stacks and can be developed further. The goal is to create more complex systems, infrastructure, and machine learning, such as distributed load, automatic delivery system and trackings, and natural language processing and so on.
2. To produce template of Frontend codes, I used vercel's AI combined with Cursor's AI, but as the real project uses API call, I mainly coded them all by writing it manually rather than using copy paste strategy. The purpose is to absorb knowledge of pattern Frontend codes, and memorize the coding style of the Frontend.
3. Studied several codecademy courses of Frontend such as:
   - Learn React: Introduction Course
   - Learn JavaScript​: Asynchronous Programming by Codecademy
4. I completed the projects locally on 18 July 2025, where later I need to deploy the features to production for my shareable portfolio.
