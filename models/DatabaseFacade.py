from sqlalchemy import select
from db import DatabaseConnector, db
from db_models import User, Jets, Rentals


class DatabaseFacade:
    def __init__(self):
        self.connector = DatabaseConnector()

    def fetch_all_jets(self):
        jets_query = select(Jets).filter()
        jets = db.session.execute(jets_query).scalars().all()
        return jets

    def fetch_jet_by_id(self,jet_id):
        jet = db.session.query(Jets).get(jet_id)
        return jet


    def fetch_all_available_jets(self):
        jets_query = select(Jets).filter(Jets.state == 'available')
        jets = db.session.execute(jets_query).scalars().all()
        return jets

    def fetch_all_users(self):
        return db.session.query(User).all()

    def add_user(self, username, email, password, full_name):
        user = User(username=username, email=email, password=password, full_name=full_name)
        self.connector.db.session.add(user)
        self.connector.db.session.commit()

        return user

    def fetch_user_rented_jets(self, user_id):
        rented_jets = db.session.query(Rentals).filter_by(user_id=user_id).all()
        return rented_jets

    def fetch_all_rented_jets(self):
        rented_jets = db.session.query(Rentals).all()
        return rented_jets

    def delete_jet(self, jet_id):
        jet = db.session.query(Jets).get(jet_id)
        if jet:
            db.session.delete(jet)
            db.session.commit()

    def delete_rental(self, rental_id):
        rental = db.session.query(Rentals).get(rental_id)
        if rental:
            jet_id = rental.jet_id

            # Update the status of the jet to 'available'
            jet = db.session.query(Jets).get(jet_id)
            if jet:
                jet.state = 'available'
                db.session.commit()
            else:
                print(f"Jet {jet_id} not found")

            # Delete the rental after updating the jet state
            db.session.delete(rental)
            db.session.commit()

    def delete_user_by_id(self, user_id):
        user = db.session.query(User).get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()

    def fetch_rental_by_id(self, rental_id):
        rental = db.session.query(Rentals).get(rental_id)
        return rental

    def delete_jet_by_id(self, jet_id):
        jet = db.session.query(Jets).get(jet_id)
        if jet:
            db.session.delete(jet)
            db.session.commit()

    def fetch_user_by_id(self, user_id):
        user = db.session.query(User).get(user_id)
        return user
