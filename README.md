# ITEM-CATALOG-APP
creator: Sayam Sawai
This is a Project Work

# About Item Catalog
Item catalog is simple RESTful CRUD app where users can read, create,add and delete Items. The items are placed according to their categories. You can add more categories as well

# Technology Stack
Python
Flask
Sqlalchemy
Ajax
Html
CSS

# Installation 
You have to download some dependencies and follow some instructions to get the App running

## Dependencies
- [Vagrant]("https://www.vagrantup.com/")
- [Virtual box 14]("https://www.virtualbox.org/wiki/Downloads")

## Go to http://console.developers.google.com/ and setup your account
1. Create a project
2. Go the the credentials page
3. click on create credentials and then ouath client id
4. Add Authorized Javascript origins - http://localhost:5000/
5. Add Authorized redirect URLs - http://localhost:5000/home
6. Click on download JSON 
7. Copy the JSON file to the /catalog folder and rename it to 'client.json'
8. Copy your Client id given by google and paste it in the login.html(on line 26) file in templates folder

# Installation Process
1. Install both Vagrant and Virtual box
2. Clone the full-stack-vm-master file you downloaded 
3. Go to the vagran/catalog folder
4. Launch Vagrant using vagrant up
5. log into vagrant using vagrant ssh
6. change director to /vagrant using cd /vagrant
7. Run the setup_database_itemcatalog.py using python2
8. Run the database_populate.py using python2
9. Run the app using item_catalog_backend.py using python2
10. Go to http://localhost:5000/ to access the app

# JSON
to get all the items and categories
go to /JSON/catalog

to get only categories
go to /JSON/category

to get only items
go to /JSON/item

# CODE FROM THIRD PARTY RESOURCES
https://stackoverflow.com/questions/50011349/return-joined-tables-in-json-format-with-sqlalchemy-and-flask-jsonify
to get Some insight about how to properly show all the json data in a serialized manner

 
