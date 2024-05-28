class Subject:
    def __init__(self):
        self._observers = []
        self.notifications = []

    def register(self, observer):
        self._observers.append(observer)

    def unregister(self, observer):
        self._observers.remove(observer)

    def notify_observers(self, data=None):
        for observer in self._observers:
            observer.update(data)
            self.notifications.append(observer.format_notification(data))


class UserObserver:
    def update(self, data):
        # Logic to notify regular users about new jets added
        print(f"New jet added: {data['jet_model']}")

    def format_notification(self, data):
        return f"New jet added: {data['jet_model']}"


class AdminObserver:
    def update(self, data):
        # Logic to notify admins about jet rentals
        if 'user_id' in data:
            if data['user_id'] is not None:
                print(f"Jet rented: {data['jet_model']} by user {data['user_id']}")
            else:
                print(f"Jet rented: {data['jet_model']}")

    def format_notification(self, data):
        if 'user_id' in data:
            if data['user_id'] is not None:
                return f"Jet rented: {data['jet_model']} by user {data['user_id']}"
            else:
                return f"Jet rented: {data['jet_model']}"
        else:
            return "Jet created"
