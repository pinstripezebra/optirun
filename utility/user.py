from flask_login import LoginManager, UserMixin

# A basic user data model
class User(UserMixin):
    def __init__(self, username, password, latitude, longitude, optimal_conditions):
        self.id = username
        self.password = password
        self.latitude = latitude
        self.longitude = longitude
        self.optimal_conditions = optimal_conditions
