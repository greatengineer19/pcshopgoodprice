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
1. FastAPI (v0.115)
2. Python (v3.9)
3. Pytest (Testing framework)
4. SQL Alchemy (Database toolkit)
5. Pydantic (API Schema tools)
6. Apscheduler (Job scheduling tools for FastAPI)
7. PostgreSQL (v17.5)
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

## Why FastAPI?
In February 2025, I visualized my needs for learning AI, or LLM, or Data Science which mainly used Python for the development. Lots of companies are using either Go, Python, Ruby, Java for the backend, and because I want to learn one language that can be used interchangeably for backend and AI development, I choose to learn Python.
Asked chatGPT for the list of popular frameworks of Python used by tech companies, and chooses FastAPI over Django or Flask because the name 'Fast' in it and less configuration that other frameworks.

## Product Summary
### Login as Buyer
There are three features that buyer can do:
- Shop\
As a buyer, sellable products are listed here with 2 columns per row that's showing the image, name, price after discount and reviews.
Buyer can filter which products needs to be displayed, clicking on each product to direct user to detailed product page.
The detail product page will consist of details of specifications, prices, and quantities for user to add to cart or buy directly
- Cart\
The cart will list out all items user have added and not yet paid, where user can add or delete quantities, choose payment method to pay the order.
And fill out address details for delivering the items.
- Orders\
Unpaid order, paid invoices, and sales deliveries of the user will be listed with the sequence of Unpaid orders a.k.a Sales Quote, Sales Delivery, and Sales Invoice as the last sequence.
User can see the details, address, and recipient, and tracking information of the package they've bought, as well as order status and order no.

### Login as Seller
Seller, alias Admin have four features:
- Management of Computer Components\
Seller can add, edit, delete computer components, define price based on day (Monday, Tuesday, ... Sunday).
Add one image each product, which is mainly needed for a good sales.
- Purchase Invoice Recording\
Seller can record the purchase they made to the Vendor of the computer components they've listed at their store.
Purchase Invoice can have invoice date, list of items, and expected inbound delivery date.
- Inbound Delivery Recording\
Received items will be recorded here. There will be a received quantity, or damaged quantity if the item is not in a good condition.
Delivery reference, and once it is created the delivery will be assigned status Completed, and will have inventory in_stock.
- Report Purchase Invoices and Report Stock Movement\
All items that have been purchased to the vendor can be tracked in the report purchase invoices.
There are filters helping the seller to adjust which invoice or product they want to see.
And the report stock movement to record SalesDelivery and InboundDelivery, mainly to calculate the current stock, the needs to purchase more products,
or to adjust prices based on historical demands.

## Project Timeline
1. 1st March 2025, I began to learn about Python FastApi, Next.JS, and Docker for this self-project. The idea of building the e-commerce project was because I need to learn new stacks of programming language, and the project must be able to be used by all those stacks and can be developed further. The goal is to create more complex systems, infrastructure, and machine learning, such as distributed load, automatic delivery system and trackings, and natural language processing and so on.
2. To produce template of Frontend codes, I used vercel's AI combined with Cursor's AI, but as the real project uses API call, I mainly coded them all by writing it manually rather than using copy paste strategy. The purpose is to absorb knowledge of pattern Frontend codes, and memorize the coding style of the Frontend.
3. Studied several codecademy courses of Frontend such as:
   - Learn React: Introduction Course
   - Learn JavaScript​: Asynchronous Programming by Codecademy
4. I completed the projects locally on 18 July 2025, where later I need to deploy the features to production for my shareable portfolio.
