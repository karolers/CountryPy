import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import datetime
import getpass

table = pd.read_csv("final_food_iati_capital.csv")

print("""\n Let me guess, you want to run away from IronHack and go somewhere new but don't have the brains to decide?
        Don't worry! We all feel the same, we got you!!!""")

date_b = input('\n Tell me, when are you thinking of going? (YYYY-MM-DD) ')
date_r = input('\n And when do you plan to come back? (YYYY-MM-DD) ')
budget = float(input('\n And how much money do you have to spend there? '))
budget_food = budget*0.33
travel_time = (datetime.datetime.strptime(date_r,'%Y-%m-%d')-datetime.datetime.strptime(date_b,'%Y-%m-%d')).days

""" CHECK FOODING"""
table_budget = table[table['price']*2*travel_time < budget_food]
table_budget = table_budget.sample(frac=1)
code_list = list(table_budget['code'].head(5))

print('\n Please be patient, we are looking all over the world! ')

""" CHECK FLIGHTS"""
from requests.auth import HTTPBasicAuth
import getpass
url="https://developers.amadeus.com/my-apps/orbitfly"
password = getpass.getpass()
response = requests.post(url=url,auth=HTTPBasicAuth("Bewek Bastola",password))
response=requests.post(url=url)

from amadeus import ResponseError, Location, Client
amadeus = Client(
    client_id='IBcYKGqcwh0hzDXldNCWk9l4iZP9AkhH',
    client_secret='TYxCgbyLitTM6ydO'
)

dict= {}
final_list=[]
for airp in code_list:
    response = amadeus.shopping.flight_offers_search.get(
            originLocationCode='LIS',
            destinationLocationCode= airp,
            departureDate='2022-11-01',
            returnDate='2022-12-01',
            adults=2)
    data = response.data

    prices = [i['price'] for i in data]
    prices_df = pd.DataFrame.from_dict(prices)

    dict = {'airp_code' : airp, 'min_price' : prices_df['total'].min()}
    final_list.append(dict)

flights_df = pd.DataFrame(final_list)
food_flight_df = pd.merge(left=flights_df, 
                            right=table, 
                            how='inner',
                            left_on='airp_code', 
                            right_on='code').rename(columns={'price':'food_price','min_price':'flight_price',
                            'Countries':'countries'}).drop(columns=['label', 'city', 'code'])

"""CHECK ACCOMMODATION"""
accom_df = pd.read_csv("acommodation.csv")
final_df = pd.merge(left=food_flight_df, 
                    right=accom_df, 
                    how='inner', 
                    left_on='countries', 
                    right_on='country').rename(columns={'price':'accom_price'})

final_df ["column"] = final_df["food_price"].astype(float) + final_df["flight_price"].astype(float) + (final_df["accom_price"].astype(float)*travel_time)

"""CALCULATION DECISION"""
def ok_nok(x):
    if x <= budget:
        return 'OK'
    else:
        return 'NOK'

final_df['decision'] = final_df['column'].apply(ok_nok)

final_df["decision"].value_counts()

c = final_df[final_df["decision"] == 'OK']
c = c.drop_duplicates()
c.rename(columns={'column':'final cost'}, inplace=True)

"""PRINTING DECISION"""
if len(c) == 0:
    print("\n Upsss, you don't have money enough... looks like you'll have to wait for you data job!")
else:
    print("""This are your options, say thanks! \n
            Day of departure: """, date_b, """
            Day of return: """, date_r, """
            Number of happy days: """, travel_time, """
            Original budget: """, budget,"""€ \n""")
    print(c[["country","capital","final cost"]])
    print("""\n Can't make up your mind?
        We'll make up your flight! @countryPy""")