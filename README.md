# PCSHOPGOODPRICE
## BUYER AND SELLER PLATFORM, AN ONLINE COMPUTER SHOP

&nbsp;
&nbsp;
&nbsp;

## Table of Contents
* [Tech stacks](#tech-stacks)
* [Pytest (Tested them all!)](#pytest-tested-them-all)
* [Project Structure](#project-structure)
* [Why FastAPI?](#why-fastapi)
* [Product Summary](#product-summary)
* [Project Timeline](#project-timeline)

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
In February 2025, I visualized my needs for learning AI, or LLM, or Data Science which mainly used Python for the development. Lots of companies are using either Go, Python, Ruby, Java for the backend, and because I want to learn one language that can be used interchangeably for backend and AI development, I choose to learn Python.\
I Asked chatGPT for the list of popular frameworks of Python used by tech companies, and I choose FastAPI over Django or Flask because it has the name 'Fast' in it and less configuration than other frameworks.

As a guy who mainly codes with Ruby on Rails, which uses Object Oriented Programming pattern, or a Model, Controller, and Service architecture, Python's introduced more similarities and easier to learn rather than other programming languages. It helps me to focus on the task and get things done quickly with the minimum free time that I have each week. While similar, I still need to adapt to it's "explicit is better than implicit" programming pattern such as:
```python
ratings_query = self.db.query(
                    ComputerComponentReview.component_id,
                    func.count(ComputerComponentReview.id).label('count_review_given'),
                    func.avg(ComputerComponentReview.rating).label('avg_rating')
                ).filter(
                    ComputerComponentReview.component_id.in_(self.component_ids)
                ).group_by(
                    ComputerComponentReview.component_id
                )

# Create ratings dictionary with proper default values
ratings = {
    r.component_id: {
        'rating': round(float(r.avg_rating), 2) if r.avg_rating is not None else 0.0,
        'count_review_given': int(r.count_review_given) if r.count_review_given is not None else 0
    } 
    for r in ratings_query
}
```

The above code snippet needs to explicitly state the: "self.db", "func.avg", "label" and not as a built-in function that's given by the Python.
In ruby on rails, I can made it similarly with:
```ruby
rq = ComputerComponentReview.where(component_id: component_ids).group(:component_id).select("component_id, count(id) AS count_review_given, avg(rating) as rating").as_json

ratings = rq.reduce({}) do |agg, val|
    agg.merge({ val['component_id'] => { 'rating' => val['rating'].to_d.round, 'count_review_given' => val['count_review_given'].to_i }
end
```

Though, I've evolved and build things to be more explicit, decoupling logic to allow for independent unit tests.

## Product Summary
### Login as Buyer
There are three features that buyer can do:
- Shop\
As a buyer, sellable products is a feature of choosing your item and adding it to the basket. It displays all items that's sellable, show prices before and after discount, rating given by the customers that previously bought the items. You are given a wide range of filters such as categories, prices, and rating to help you filter the item you only want to buy.
- Cart\
The cart is a feature where after buyer chooses the item they wants to purchase, yet they keep it for some period of time. Like a wishlist, or a list of products that's been saved and will be checked out or paid later.
User can choose the payment method they wanna use, input address, and proceed to pay the bills. As this is a demo feature, there's no actual payment made.

    For now, after you proceed to pay the bills, the Quotation can be paid manually by clicking "Paid quotation", and the demo app will delete the Quotation and create Sales Invoice for you.
- Orders (Sales Quote, Sales Invoice, Sales Delivery)\
Is a list of orders you have purchased, a historical data, all for you. In the beginning, you will have a Sales Quote, which as Quotation that enlisted items you ordered, but waiting for you to make a full payment. You can also choose to cancel the orders, and the record will be deleted and will not be returned to the cart.

    Sales Invoice is a feature of paid Sales Quotes. It stated the invoice number and sales quote no, and status will be "Pending" or "Completed". A paid sales invoice will start as "pending", and you will have no authorization to change the state of the invoice, while the background tasks will check the pending invoice every 30 seconds, and perform Sales Delivery creation which will change the invoice status into "completed".
Sales Invoice which is completed means the store or PCSHOPGOODPRICE is delivering the items to your address.

    Sales Delivery is a feature of delivering the items. It will have next major updates of live tracking delivery, but for now you will only be given a choice to fully delivered the items or void.
If it's fully delivered, then the action will create an Inventory consists of product and quantities that will deduct the stock of PCSHOPGOODPRICE. Seller can see the records in inventories report.

### Login as Seller
Seller, alias Admin have four features:
- Management of Computer Components\
Computer Components is an alias of Products. It's computer components because I want it to sell only components. Items which is assembled such as Custom PC will later have a feature called computer_component_groups, with the items combined of computer components record. Seller can add, edit, and delete record that's not yet have associations, adjust selling prices based on day such as Monday, Tuesday, Wednesday, etc.. In the future if there are multiples special day such as New Year, 7/7, 8/8 I can add the feature into it so that the selling prices will follow the setting.

- Purchase Invoice\
Purchase Invoice is a feature of purchasing or procuring a computer components to Vendor. It includes filling invoice date, manual textbox of supplier name, expected delivery date. The beginning of the status is pending.
You can delete it, or wait until inbound delivery action and change the status of purchase invoice to completed.

- Inbound Delivery Recording\
Is a list of inbound records from Vendor. Vendor will send items to PCSHOPGOODPRICE, and PCSHOPGOODPRICE will record the items, categorize it as well received or damaged, input the delivery date and receiver of the items.
Seller is allowed to adjust the records by deleting it, or adding pictures of receiving goods.

If an item is received, an Inventory of stock in will be created by the input of delivery date, and can be seen in report inventory movement
<img width="1123" height="767" alt="Screenshot 2025-08-03 at 14 10 32" src="https://github.com/user-attachments/assets/f65f3de2-8d46-46c3-ae03-08bed4ab7bc6" />

- Report Purchase Invoices\
Is a history of products that you have purchased to Vendor. You can use filter such as invoice number, component or category name, invoice date or status to filter products you want.

- Report Inventory Movement\
Is a history of Inbound Deliveries received and Sales Deliveries fully received. Inbound Delivery will add stock to PCSHOPGOODPRICE, while Sales Delivery will reduce stock.
The order of reports as follow:
    - Category Name
    - Component Name
    - Stock Date
    - ID
By the order of reports, you can see the quantity movement of the stocks by row.
Seller can also adjust the data shown by using filter

## Project Timeline
1. In 1st March 2025, I realized my needs to study ML, AI, Frontend, DS, and other backend language. Reading article or watching youtube will not make me master things fully, and because I'm curious to build my own product, I am then thinking of creating an online computer shop where I can be the admin, and I can set up the store myself. Computer shop is a good beginning since it's not common topic for engineers to build as a side project. Engineers are often drawn to small, independent projects that let them customize a tool and explore its capabilities, but to further add more tech stacks into the project, small project is not enough, I need a project where I visualized that it's used by real people, 1 or thousand, or even millions, and can have multiple tech stacks in it. This led me to choose React's Next JS and Python's FastAPI for the backend.
3. Firstly, I began by setting up local development, connecting the PostgreSQL, Docker, Python and React together. This was a significant learning curve, as I had to re-learn Docker, and Python FastAPI from documentation as well as AI chatbot such as Gemini. With limited time to learn Frontend, I used v0.dev to generate code skeletons, which I then write it manually without any copy paste, and refactor the codes to call API to backend, separating codes into services, and building asynchronous programming.
4. Aside of working and this side project, I am also interested in playing Fantasian and Dota2, and going out with friends and families. This meant I sometimes had to rotate my activities to stay motivated and avoid burnout.
### Learning and Development
From April to May 2025, I improved my frontend knowledges by learning in Codecademy:
    - Learn React: Introduction Course
    - Learn JavaScript​: Asynchronous Programming by Codecademy

### Project Milestones
**April - May 2025**: I spent 2 months to complete the "Seller Side" features.
**May - June 2025**: Prompt the frontend skeletons of the "Buyer Side", finished the buyer side features
**July - August 2025**: 
1. I dedicated this period to refactoring the entire Backend and Frontend codebase. Drawing on my 4 years experience as backend engineer, I made the code more readable and well-written.
2. Setting up the production infrastructure such as AWS and Vercel. This involves to learn about subnets, routing table, internet gateway, application load balancer, A record and CNAME, CORS between Vercel and ALB, and finally to document the project I have created

### Thank you for
A great friend of mine, the first person that I introduced my product into, as she reviewed the product carefully, helps me to further improve the quality of the product as of now. Thank you :)
