from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import crud, models, schemas
from database import SessionLocal, engine
import zmq, json

context = zmq.Context() # Here, Context serves as the container for all ZeroMQ sockets 

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
socket = context.socket(zmq.REQ) # REQ sockets are used to send requests
socket.connect("tcp://localhost:5555")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class StripeWebhookData(BaseModel):
    object: dict[str, str | int | bool | list|  dict[str, str | int | bool | list | None] | None] | None = None
    previous_attributes: dict[str, str | None ] | None = None

# Request object schema which we get from Stripe webhook
class StripeWebhookEvent(BaseModel):
    id: str | None = None
    type: str | None = None
    object: str | None = None
    api_version: str | None = None
    created : int | None = None
    request: dict[str, str | None] | None = None
    livemode : bool | None = None
    pending_webhooks : int | None = None
    data: StripeWebhookData | None = None



@app.get("/")
def root():
    return {"message": "Open Docs at /docs or /redoc to see the API documentation"}


@app.post("/customers/")
def create_customer(customer: schemas.Customer, db: Session = Depends(get_db)):
    db_customer = crud.get_customer_by_email(db, email=customer.email)
    if db_customer:
        raise HTTPException(status_code=400, detail="Email already registered")
    socket.send(b"create-" + bytes(customer.toJSON(), encoding='utf8'))
    message = socket.recv()
    print("Received reply - %s" % (message.decode("utf-8")))
    return crud.create_customer(db=db, customer=customer)

@app.put("/customers/")
def edit_customer(customer: schemas.Customer, db: Session = Depends(get_db)):
    db_customer = crud.get_customer_by_email(db, email=customer.email)
    if not db_customer:
        raise HTTPException(status_code=400, detail="Email doesn't exist")
    socket.send(b"update-" + bytes(customer.toJSON(), encoding='utf8'))
    message = socket.recv()
    print("Received reply - %s" % (message.decode("utf-8")))
    return crud.edit_customer_by_email(db=db, customer=customer)

@app.get("/customers/")
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    customers = crud.get_customers(db, skip=skip, limit=limit)
    socket.send(b'read-{"all":"all"}')
    message = socket.recv()
    return {"customers": customers, "stripeList": json.loads(message.decode('utf-8'))}


@app.get("/customers/{customer_id}")
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = crud.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    socket.send(b"get-" + bytes(json.dumps(db_customer.toDict()), encoding='utf8'))
    message = socket.recv()
    print("Received reply - %s" % (message.decode("utf-8")))
    return {"customer":db_customer, "stripeCustomer": json.loads(message.decode('utf-8'))}

@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = crud.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    socket.send(b"delete-" + bytes(json.dumps(db_customer.toDict()), encoding='utf8'))
    message = socket.recv()
    print("Received reply - %s" % (message.decode("utf-8")))
    return crud.delete_customer_by_email(db=db, customer=db_customer)

@app.post("/stripe-webhook")
async def stripe_webhook(event: StripeWebhookEvent, db: Session = Depends(get_db)):
    try:
        if event.type == "customer.created":
            db_customer = crud.get_customer_by_email(db, email=event.data.object["email"])
            if db_customer:
                return {"message": "Customer is already registered"}
            customer = schemas.Customer(email=event.data.object["email"], name=event.data.object["name"])

            return crud.create_customer(db=db, customer=customer)

        if event.type == "customer.updated": # Cross checking for update in only name, only email, both
            if "email" in event.data.previous_attributes:
                customer = schemas.Customer(email=event.data.previous_attributes["email"], name=event.data.object["name"])
                crud.delete_customer_by_email(db=db, customer=customer)
                customer = schemas.Customer(email=event.data.object["email"], name=event.data.object["name"])
                return crud.create_customer(db=db, customer=customer)
            customer = schemas.Customer(email=event.data.object["email"], name=event.data.object["name"])
            return crud.edit_customer_by_email(db=db, customer=customer)

        if event.type == "customer.deleted":
            db_customer = crud.get_customer_by_email(db, email=event.data.object["email"])
            if not db_customer:
                return {"message": "Customer is already deleted"}
            customer = schemas.Customer(email=event.data.object["email"], name=event.data.object["name"])
            return crud.delete_customer_by_email(db=db, customer=customer)

        return {"message": "No test called", "event": event}
    except Exception as exc:
        print(repr(exc))
        return {"message": "Error Occured"}


# async def start_ngrok():
#     # Start Ngrok and expose the FastAPI app
#     tunnel = await ngrok.connect(8000, authtoken_from_env=True)
#     print (f"Ingress established at {tunnel}")
