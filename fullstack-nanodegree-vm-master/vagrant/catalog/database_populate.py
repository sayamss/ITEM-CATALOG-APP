# importing all the neccassary things from sqlalchemy to create new items
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from setup_database_itemcatalog import Base, User, Category, Item
import datetime
from time import strftime

engine = create_engine("sqlite:///itemcatalog.db")

# binding engine to the session
Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)
session = DBsession()

#                       CREATING USERS
# ****************************************************************
sayam = User(username="Sayam sawai",
             email="sawaisayam@gmail.com",
             picture="https://pbs.twimg.com/profile_images/"
                     "920521903042957312/TarVYQVR_400x400.jpg")
session.add(sayam)
session.commit()
# ****************************************************************
sanket = User(username="Sanket sawai",
              email="sanketsawai525@gmail.com",
              picture="https://i.ytimg.com/vi/kLAnVd5y7M4/maxresdefault.jpg")
session.add(sanket)
session.commit()
# ****************************************************************


# -----------------------------------------------------------------------------------------

#                      CREATING CATEGORYS
# ****************************************************************
smartphone = Category(Name="Smartphone", user_id=1)
session.add(smartphone)
session.commit()
# ****************************************************************
Food = Category(Name="Food", user_id=1)
session.add(Food)
session.commit()
# ****************************************************************
Cricket = Category(Name="Cricket", user_id=2)
session.add(Cricket)
session.commit()
# ****************************************************************
Laptop = Category(Name="Laptop", user_id=2)
session.add(Laptop)
session.commit()
# ****************************************************************

# ----------------------------------------------------------------------------------------

#                       CREATING ITEMS
# ****************************************************************
iphone5 = Item(Name="Iphone 5",
               description="a very good and premium phone"
                           " that was released in 2013",
               picture="https://cdn2.gsmarena.com/vv/bigpic/"
                       "apple-iphone-5se-ofic.jpg",
               id_category=1, user_id=1, time=strftime("%m/%d/%Y %H:%M"))
session.add(iphone5)
session.commit()
# ****************************************************************
note8 = Item(Name="Samsung galaxy note 8",
             description="a very high end expensive phone",
             picture="https://images.mobilefun.co.uk/graphics/"
                     "450pixelp/64782.jpg",
             id_category=1, user_id=1, time=strftime("%m/%d/%Y %H:%M"))
session.add(note8)
session.commit()
# ****************************************************************
icecream = Item(Name="Chocolate ice cream",
                description="A very delicious food item, Cold and sweet",
                picture="https://www.handletheheat.com/wp-content/uploads/"
                        "2016/05/Death-by-Chocolate-Ice-Cream-02.jpg",
                id_category=2, user_id=2, time=strftime("%m/%d/%Y %H:%M"))
session.add(icecream)
session.commit()
# ****************************************************************
chicken_gravy = Item(Name="Chicken Gravy",
                     description="A very spicy and delicious food "
                                 "based out of india",
                     picture="https://farm4.staticflickr.com/3926/"
                             "14978241939_84884b5c65_o.jpg",
                     id_category=2, user_id=2, time=strftime("%m/%d/%Y %H:%M"))
session.add(chicken_gravy)
session.commit()
# ****************************************************************
cricket_bat = Item(Name="Cricket Bat",
                   description="A bat with high stroke and good built "
                               "to hit the ball with",
                   picture="https://images-na.ssl-images-amazon.com/images/"
                           "I/21dbnuMXNhL._SL500_AC_SS350_.jpg",
                   id_category=3, user_id=1, time=strftime("%m/%d/%Y %H:%M"))
session.add(cricket_bat)
session.commit()
# ****************************************************************
cricket_ball = Item(Name="Cricket Ball",
                    description="Leather ball for cricket",
                    picture="https://upload.wikimedia.org/wikipedia/commons/"
                            "thumb/4/48/A_Cricket_Ball.jpg/"
                            "1200px-A_Cricket_Ball.jpg",
                    id_category=3, user_id=1, time=strftime("%m/%d/%Y %H:%M"))
session.add(cricket_ball)
session.commit()
# ****************************************************************
asuslaptop = Item(Name="Asus rog",
                  description="a very powerful laptop by asus",
                  picture="https://www.excaliberpc.com/images/661022_1/"
                          "large.jpg",
                  id_category=4, user_id=2, time=strftime("%m/%d/%Y %H:%M"))
session.add(asuslaptop)
session.commit()

print("done!!!!!!!!!!!!!!!")
