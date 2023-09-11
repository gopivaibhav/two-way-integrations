import json, os, schemas
import zmq, stripe
from dotenv import load_dotenv
load_dotenv() # Loading .env to use environment variables
stripe.api_key = os.getenv("STRIPE_API_KEY")

# Function to return all the Customers List available on Stripe
def getListStripe():
    return stripe.Customer.list()


# Function to Create a Customer on Stripe with the given details
def createStripeCustomer(customer: schemas.Customer):
    stripe.Customer.create(
        name = customer['name'],
        email = customer['email']
        )
    print("created customer with API")


context = zmq.Context() # Here, Context serves as the container for all ZeroMQ sockets 
socket = context.socket(zmq.REP) # REP sockets are used to receive requests
socket.bind("tcp://*:5555")

print("Server is up and running")

while True:
    #  Wait for next request from client
    message = socket.recv()

    data = json.loads(message.decode("utf-8").split('-')[1])
    operation = message.decode("utf-8").split('-')[0]

    # Operation was sent from main.py file to check the event whether to create, update, delete or get the customers.

    if(operation == "create"):
        createStripeCustomer(data)
        socket.send(b"Created - %b customer" % (bytes(data['email'], encoding='utf-8')))

    if(operation == "update"):
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
        socket.send(json.dumps(stripeCustomer, indent=2).encode('utf-8'))