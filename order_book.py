from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from models import Base, Order
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

fields = ['sender_pk','receiver_pk','buy_currency','sell_currency','buy_amount','sell_amount']

def process_order(order):
    #Your code here
    
    #Insert order into data base
    
    new_order = Order(**{f:order[f] for f in fields})
    session.add(new_order)
    session.commit()
    
    #Check if there are any existing orders that match the new order
    orders = session.query(Order).filter(Order.filled == None).all()
    
    for existing_order in orders:
        
        # Check if currencies match
        if existing_order.buy_currency == order.sell_currency and existing_order.sell_currency == order.buy_currency:
           
            # Check if exchange rates match
            if existing_order.sell_amount * new_order.sell_amount >= new_order.buy_amount * existing_order.buy_amount:
                
                #If a match is found between order and existing_order do the trade
                existing_order.filled = datetime.now()
                new_order.filled = datetime.now()
                existing_order.counterparty_id = new_order.get(id)
                new_order.counterparty_id = existing_order.get(id)
                break
                
        if existing_order.buy_amount > new_order.sell_amount:
            #create order
            print("create new order")
            
            buy_amount = existing_order.buy_amount - new_order.sell_amount
            sell_amount = existing_order.sell_amount / existing_order.buy_amount * buy_amount
            
            child_order = {'buy_currency': existing_order.buy_currency,
                           'sell_currency': existing_order.sell_currency,
                           'buy_amount': buy_amount,
                           'sell_amount': sell_amount,
                           'sender_pk': existing_order.sender_pk,
                           'receiver_pk': existing_order.receiver_pk
                          }
            
            elif new_order.buy_amount > existing_order.sell_amount:
                #create order
                print("create new order")
                
