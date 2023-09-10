from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Open Docs at /docs or /redoc to see the API documentation"}

@app.post("/customers/", response_model=schemas.Customer)
def create_customer(customer: schemas.Customer, db: Session = Depends(get_db)):
    db_customer = crud.get_customer_by_email(db, email=customer.email)
    if db_customer:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_customer(db=db, customer=customer)

@app.put("/customers/{customer_id}", response_model=schemas.Customer)
def edit_customer(customer: schemas.Customer, db: Session = Depends(get_db)):
    db_customer = crud.get_customer_by_email(db, email=customer.email)
    if not db_customer:
        raise HTTPException(status_code=400, detail="Email doesn't exit")
    return crud.edit_customer_by_email(db=db, customer=customer)

@app.get("/customers/", response_model=list[schemas.Customer])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    customers = crud.get_customers(db, skip=skip, limit=limit)
    return customers


@app.get("/customers/{customer_id}", response_model=schemas.Customer)
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = crud.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

class StripeWebhookData(BaseModel):
    object: dict[str, str | int | bool | list|  dict[str, str | int | bool | list | None] | None] | None = None


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

@app.post("/stripe-webhook")
async def stripe_webhook(event: StripeWebhookEvent):
    # Process the event (sync with your customer catalog)
    # Replace this with your synchronization logic

    # Respond to Stripe to acknowledge receipt of the event
    return {"message": "Webhook received", "event": event}

# async def start_ngrok():
#     # Start Ngrok and expose the FastAPI app
#     tunnel = await ngrok.connect(8000, authtoken_from_env=True)
#     print (f"Ingress established at {tunnel}")
