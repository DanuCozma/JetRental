
from db import db
from db_models import User, Rentals


class UserRepository:
    @staticmethod
    def delete_user(user_id):
        user = db.session.query(User).get(user_id)

        if user:
            # Check if the user has any associated rentals
            rentals = db.session.query(Rentals).filter_by(user_id=user_id).all()

            if rentals:
                # If there are associated rentals, delete them first
                for rental in rentals:
                    db.session.delete(rental)

            # Now delete the user
            db.session.delete(user)
            db.session.commit()
            return True
        else:
            return False


class RentalRepository:
    @staticmethod
    def get_rentals_by_user(user_id):
        return db.session.query(Rentals).filter_by(user_id=user_id).all()
