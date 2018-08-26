# importing flask
from flask import (Flask,
                   redirect,
                   jsonify,
                   url_for,
                   request,
                   flash,
                   render_template,
                   make_response)

from flask import session as login_session


# sqlalchemy to work with the database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from setup_database_itemcatalog import *

# importing oauth library for authentication and authorization
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# random and string for creating state
import random
import string

# httplib2 and requests for making get requests
import httplib2
import requests

# json to python and vice versa
import json
from time import strftime
# *************************************************************************************************
# connecting to the database
# ************************************************************************************************
engine = create_engine("sqlite:///itemcatalog.db?check_same_thread=False")

Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)
session = DBsession()
# ************************************************************************************************

# flask instance
item_catalog = Flask(__name__, template_folder="template")

# retrieving client id from client_Secrets.json file
# ***********************************************************************************************
CLIENT_ID = json.loads(open("client.json", 'r').read())['web']['client_id']
# **********************************************************************************************


# Creating a login route
# ***********************************************************************************************
@item_catalog.route("/login")
def login():
    '''
    Creating a state token consisting of uppercase
    characters and digits, length: 32
    '''
    state = ''.join(
                    random.choice(string.ascii_uppercase + string.digits)
                    for x in range(40)
                )
    login_session['state'] = state
    # rendering login.html and passing in the state
    return render_template("login.html", STATE=state)
# ************************************************************************************************


# ************************************************************************************************
@item_catalog.route("/googleconnect", methods=['POST'])
def googleconnect():

    # Check for a Valid state token
    if request.args.get("state") != login_session['state']:
        response = make_response(json.dumps(
                                 "STATE DOES NOT MATCH , TRY LOGGING IN AGAIN"
                                 ), 401)
        response.headers['Content-Type'] = "application/json"
        return response

    # collect the authorization code
    authcode = request.data

    try:
        # Try to exchange the auth code with an access_token
        oauthflow = flow_from_clientsecrets("client.json", scope="")
        oauthflow.redirect_uri = "postmessage"
        credentials = oauthflow.step2_exchange(authcode)

    except FlowExchangeError:
        # return a json response when there is an error while exchanging
        response = make_response(json.dumps(
                                 "FAIL TO EXCHANGE AUTHCODE WITH ACCESS TOKEN")
                                 )
        response.headers['Content-Type'] = "application/json"
        return response

    # store the access token
    access_token = credentials.access_token

    # Send a request and parse it
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # abort if there is an error in the result.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # verify that the access token is intented for the user.
    gplus_id = credentials.id_token['sub']

    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("the tokens user id doesnt match  the user id."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # check that the access token is valid for our app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps(
                "client id of token does not match the apps client_id"), 401
            )
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                                 'CURRENT USER IS ALREADY LOGGED IN.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # store the access token and id for using later
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Send a GET request for getting User info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {"access_token": credentials.access_token, "alt": "json"}
    answer = requests.get(userinfo_url, params=params)

    data = json.loads(answer.text)

    # Store all the user details in login session
    login_session['provider'] = "google"
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['picture'] = data['picture']

    # check if the user already exists, if not, create one
    user_id = getuserid(login_session['email'])
    if not user_id:
        user_id = createuser(login_session)
    login_session['user_id'] = user_id

    # Send a successfuly login message
    opt = "WELCOME %s" % login_session['username']
    flash("You are now logged in as %s" % login_session['username'] +
          ", Have fun with our app")
    return opt
# ***************************************************************************************************


# ***************************************************************************************************
# Create a new user using details from login session
def createuser(login_session):
    newuser = User(username=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newuser)
    session.commit()

    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# return User information takeing user's ID as argument
def getuserinfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# return user's ID taking users email as argument or return none
def getuserid(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id

    except:
        return None
# ****************************************************************************************************


# googledisconnect to let users logout
# ****************************************************************************************************
@item_catalog.route("/googledisconnect")
def googledisconnect():
    # get the current access toke
    access_token = login_session.get('access_token')

    # if access token is none, return a json response
    if access_token is None:
        response = make_response(json.dumps('Current user is not logged in.' +
                                            str(access_token)), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # send a get request to revoke the access token
    result = requests.post(
                           'https://accounts.google.com/o/oauth2/revoke',
                           params={'token': login_session['access_token']},
                           headers={'content-type':
                                    'application/x-www-form-urlencoded'}
                           )

    # store the response in status_code
    status_code = getattr(result, 'status_code')

    # check if the request was successful and reset all the login credentials
    if status_code == 200:
        # Reset the user's sesson.
        del login_session['provider']
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']

        return redirect("/home")

    # return a json response stating the error
    else:
        response = make_response(json.dumps("Failed to log out" +
                                            str(status_code)), 400)
        response.headers['Content-Type'] = "application/json"
        return response
# ****************************************************************************************************


# HOMEPAGE
# *****************************************************************************************************
@item_catalog.route("/home")
@item_catalog.route("/")
def home():
    # get all the data from the database and pass it to the html page
    category = session.query(Category).all()
    item = session.query(Item).order_by(Item.time.desc()).limit(3)
    if 'email' not in login_session:
        return render_template("publichome.html", category=category, item=item)

    else:
        return render_template("home.html", category=category, item=item,
                               username=login_session['username'])

# *****************************************************************************************************


# Display a specific category and its users
# *****************************************************************************************************
@item_catalog.route("/category/<int:categoryid>")
@item_catalog.route("/category/<int:categoryid>/")
def displaycategory(categoryid):
    category = session.query(Category.Name).filter_by(
                                           id=categoryid).one_or_none()
    name = ''.join(category)
    item = session.query(Item).filter_by(id_category=categoryid)

    return render_template("category.html", name=name, item=item)
# *****************************************************************************************************


# For creating new categories
# *****************************************************************************************************
@item_catalog.route("/createcategory", methods=['GET', 'POST'])
@item_catalog.route("/createcategory/", methods=['GET', 'POST'])
def createcategory():

    # check if user is logged in
    if 'email' not in login_session:
        return redirect("/login")

    if request.method == "POST":
        name = request.form['name']
        userid = login_session['user_id']
        user1 = getuserinfo(userid)

        newcategory = Category(Name=name, user_id=userid, user=user1)
        session.add(newcategory)
        session.commit()
        return redirect("/home")

    if request.method == "GET":
        return render_template('createcategory.html')
# *****************************************************************************************************


# Display specific Item
# *****************************************************************************************************
@item_catalog.route("/item/<int:categoryid>/<int:itemid>")
@item_catalog.route("/item/<int:categoryid>/<int:itemid>/")
def displayitem(categoryid, itemid):
    item = session.query(Item).filter_by(id=itemid)
    user_id = session.query(Item.user_id).filter_by(id=itemid)
    owner = getuserinfo(user_id)

    # check if user is logged or the current user is the owner
    if 'email' not in login_session or owner.id != login_session['user_id']:
        return render_template("publicitem.html", item=item)

    else:
        # return the page made for owners with edit and login button
        return render_template("item.html", item=item)
# *****************************************************************************************************


# For creating new items
# *****************************************************************************************************
@item_catalog.route("/createitem", methods=['GET', 'POST'])
def createitem():
    category1 = session.query(Category).all()
    if 'email' not in login_session:
        return redirect("/login")

    if request.method == "POST":
        # get all the details from the form and create new item
        name = request.form['name']
        description = request.form['description']
        picture = request.form['picture']
        time = strftime("%m/%d/%Y %H:%M")
        category = session.query(Category).filter_by(
                                Name=str(
                                     request.form['itemcategory']
                                     )).one()
        idcategory = session.query(Category.id).filter_by(
                                               Name=category.Name).one()
        user_id = login_session['user_id']
        newitem = Item(Name=name, description=description, picture=picture,
                       time=time, category=category, id_category=idcategory,
                       user_id=user_id)
        session.add(newitem)
        session.commit()
        flash("Successfully created the item")
        return redirect("/home")

    else:
        return render_template("createitem.html", category=category1)
# *****************************************************************************************************


# For editing Item
# *****************************************************************************************************
@item_catalog.route("/edititem/<int:categoryid>/<int:itemid>",
                    methods=['GET', 'POST'])
@item_catalog.route("/edititem/<int:categoryid>/<int:itemid>/",
                    methods=['GET', 'POST'])
def edititem(categoryid, itemid):
    item = session.query(Item).filter_by(id=itemid).one()
    itemcategory = session.query(Category)
    iduser = session.query(Item.user_id).filter_by(id=itemid)
    user_id = iduser
    owner = getuserinfo(user_id)

    # CHECK IF THE CURRENT USER IS OWNER OR IF USER IS LOGGED IN OR NOT
    if 'email' not in login_session or owner.id != login_session['user_id']:
        flash("You are not Authorized to  edit Item:" + item.Name + "<br>" +
              "Authorization Rights: " + owner.username)
        return redirect("/home")

    if request.method == "POST":
        item.time = strftime("%m/%d/%Y %H:%M")
        if request.form['name']:
            item.Name = request.form['name']

        if request.form['description']:
            item.description = request.form['description']

        if request.form['picture']:
            item.picture = request.form['picture']

        if request.form['itemcategory']:
            category = session.query(Category).filter_by(
                                              Name=str(
                                                   request.form[
                                                    'itemcategory'
                                                   ]
                                                   )).one()
            categoryid = session.query(Category.id).filter_by(
                                                   Name=category.Name
                                                   )
            item.category = category
            item.id_category = categoryid

        session.commit()
        flash("Successfully Edited Item: " + item.Name)
        return redirect("/home")

    if request.method == "GET":
        return render_template("edititem.html", item=item,
                               category=itemcategory)
# *****************************************************************************************************


# for deleting any specific item
# *****************************************************************************************************
@item_catalog.route("/deleteitem/<int:categoryid>/<int:itemid>",
                    methods=['GET', 'POST'])
@item_catalog.route("/deleteitem/<int:categoryid>/<int:itemid>/",
                    methods=['GET', 'POST'])
def deleteitem(categoryid, itemid):
    item = session.query(Item).filter_by(id=itemid).one()
    iduser = session.query(Item.user_id).filter_by(id=itemid)
    owner = getuserinfo(iduser)

    # CHECK IF THE CURRENT USER IS OWNER OR IF USER IS LOGGED IN OR NOT
    if 'email' not in login_session or owner.id != login_session['user_id']:
        flash("You are not Authorized to  delete Item:" +
              item.Name + "<br>" + "Authorization Rights: " + owner.username)
        return redirect("/home")

    if request.method == "POST":
        session.delete(item)
        session.commit()
        flash("Successfully Deleted The Item")
        return redirect("/home")

    if request.method == "GET":
        return render_template("deleteitem.html", item=item)

# *****************************************************************************************************


# JSON
# *****************************************************************************************************
@item_catalog.route("/JSON/category")
@item_catalog.route("/JSON/category/")
def categoryJSON():
    categories = session.query(Category).all()
    return jsonify(Categories=[a.serialize for a in categories])


@item_catalog.route("/JSON/item")
@item_catalog.route("/JSON/item/")
def itemJSON():
    item = session.query(Item).all()
    return jsonify(Items=[i.serialize for i in item])


@item_catalog.route("/JSON/catalog")
@item_catalog.route("/JSON/catalog/")
def catalogJSON():
    categories = session.query(Category).options(joinedload(
                                                  Category.items
                                                  )).all()
    return jsonify(
            dict(
             catalog=[dict(
                      c.serialize, items=[i.serialize for i in c.items])
                      for c in categories]))
# *****************************************************************************************************


@item_catalog.route("/JSON/item/<int:itemid>")
@item_catalog.route("/JSON/item/<int:itemid>/")
def specificitem(itemid):
    item = session.query(Item).filter_by(id=itemid).all()
    return jsonify(item=[i.serialize for i in item])


@item_catalog.route("/JSON/category/<int:categoryid>")
@item_catalog.route("/JSON/category/<int:categoryid>/")
def specificcat(categoryid):
    category = session.query(Category).filter_by(id=categoryid).all()
    return jsonify(category=[c.serialize for c in category])

if __name__ == '__main__':
    item_catalog.secret_key = "special key"
    item_catalog.debug = True
    item_catalog.run(host='0.0.0.0', port=5000)
