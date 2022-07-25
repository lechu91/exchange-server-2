from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from models import Base, Order
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

fields_basic = ['sender_pk','receiver_pk','buy_currency','sell_currency','buy_amount','sell_amount']
fields_child = ['sender_pk','receiver_pk','buy_currency','sell_currency','buy_amount','sell_amount','creator_id']

def process_order(order, child=False):
    #Your code here
    
    #Insert order into data base

    if child:
        new_order = Order(**{f:order[f] for f in fields_child})
    else:
        new_order = Order(**{f:order[f] for f in fields_basic})
            
    session.add(new_order)
    session.commit()
    
    #Check if there are any existing orders that match the new order
    orders = session.query(Order).filter(Order.filled == None).all()
    
    for existing_order in orders:
        
        # Check if currencies match
        if existing_order.buy_currency == new_order.sell_currency and existing_order.sell_currency == new_order.buy_currency:

            # Check if exchange rates match
            if existing_order.sell_amount * new_order.sell_amount >= new_order.buy_amount * existing_order.buy_amount:
                
                #If a match is found between order and existing_order do the trade
                existing_order.filled = datetime.now()
                new_order.filled = datetime.now()
                existing_order.counterparty_id = new_order.id
                new_order.counterparty_id = existing_order.id
                session.commit()
                break
                    
    if existing_order.buy_amount > new_order.sell_amount:
        #create order

        buy_amount = existing_order.buy_amount - new_order.sell_amount
        sell_amount = existing_order.sell_amount / existing_order.buy_amount * buy_amount

        child_data = {'buy_currency': existing_order.buy_currency,
                       'sell_currency': existing_order.sell_currency,
                       'buy_amount': buy_amount,
                       'sell_amount': sell_amount,
                       'sender_pk': existing_order.sender_pk,
                       'receiver_pk': existing_order.receiver_pk,
                       'creator_id': existing_order.id
                      }
        
        process_order(child_data, True)
        
#         child_order = Order(**{f:child_data[f] for f in fields_child})
#         session.add(child_order)
#         session.commit()

    elif new_order.buy_amount > existing_order.sell_amount:
        #create order

        buy_amount = new_order.buy_amount - existing_order.sell_amount
        sell_amount = new_order.sell_amount / new_order.buy_amount * buy_amount

        child_data = {'buy_currency': new_order.buy_currency,
                       'sell_currency': new_order.sell_currency,
                       'buy_amount': buy_amount,
                       'sell_amount': sell_amount,
                       'sender_pk': new_order.sender_pk,
                       'receiver_pk': new_order.receiver_pk,
                       'creator_id': new_order.id
                      }
        
        process_order(child_data, True)
        
#         child_order = Order(**{f:child_data[f] for f in fields_child})
#         session.add(child_order)
#         session.commit()
            
        
            
            

                
