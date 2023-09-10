from sqlalchemy.orm import Session

import models, schemas


def get_customer(db: Session, customer_id: int):
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()


def get_customer_by_email(db: Session, email: str):
    return db.query(models.Customer).filter(models.Customer.email == email).first()


def get_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Customer).offset(skip).limit(limit).all()


def create_customer(db: Session, customer: schemas.Customer):
    db_customer = models.Customer(email = customer.email, name = customer.name)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def edit_customer_by_email(db: Session, customer: schemas.Customer):
    db_edit = db.query(models.Customer).filter(models.Customer.email == customer.email).first()
    db_edit.name = customer.name
    db.commit()
    db.refresh(db_edit)
    return db_edit

def delete_customer_by_email(db: Session, customer: schemas.Customer):
    db_customer = db.query(models.Customer).filter(models.Customer.email == customer.email).first()
    db.delete(db_customer)
    db.commit()
    return {"message": "Customer deleted"}

def count_customers(db: Session):
    return db.query(models.Customer).count()