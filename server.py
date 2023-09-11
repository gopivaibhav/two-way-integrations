#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import json, os, schemas
import zmq, stripe
from dotenv import load_dotenv
load_dotenv()
stripe.api_key = os.getenv("STRIPE_API_KEY")

def getListStripe():
    return stripe.Customer.list()

def createStripeCustomer(customer: schemas.Customer):
    # print(customer['email'], customer['name'])
    stripe.Customer.create(
        name = customer['name'],
        email = customer['email']
        )
    print("created customer with API")

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

print("Server is up and running")

while True:
    #  Wait for next request from client
    message = socket.recv()
    # print("Received request: %s" % json.loads(message.decode("utf-8").split('-')[1])['name'])

    data = json.loads(message.decode("utf-8").split('-')[1])
    # time.sleep(1)
    operation = message.decode("utf-8").split('-')[0]
    if(operation == "create"):
        createStripeCustomer(data)
        socket.send(b"Created - %b customer" % (bytes(data['email'], encoding='utf-8')))

    if(operation == "update"):
        # createStripeCustomer(data)
        stripeCustomers = getListStripe()
        stripeCustomer = None
        for stripeC in stripeCustomers['data']:
            if(stripeC['email'] == data['email']):
                stripeCustomer = stripeC
                break
        stripe.Customer.modify(
            stripeCustomer['id'],
            name = data['name'],
            email = data['email']
            )
        socket.send(b"Updated - %b customer" % (bytes(data['email'], encoding='utf-8')))

    if(operation == "delete"):
        stripeCustomers = getListStripe()
        stripeCustomer = None
        for customer in stripeCustomers['data']:
            if(customer['email'] == data['email']):
                stripeCustomer = customer
                break
        print(stripeCustomer['id'])
        stripe.Customer.delete(stripeCustomer['id'])
        socket.send(b"Deleted - %b customer" % (bytes(data['email'], encoding='utf-8')))

    if(operation == "read"):
        socket.send(json.dumps(getListStripe().to_dict(), indent=2).encode('utf-8'))
    
    if(operation == "get"):
        stripeCustomers = getListStripe()
        stripeCustomer = None
        for customer in stripeCustomers['data']:
            if(customer['email'] == data['email']):
                stripeCustomer = customer
                break
        print(stripeCustomer['id'])
        socket.send(json.dumps(stripeCustomer, indent=2).encode('utf-8'))