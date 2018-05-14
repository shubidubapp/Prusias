from src import db
from time import time


class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    buildings = db.relationship('Building', back_populates="user")
    gold = db.Column(db.Float, nullable=False, default=100)
    meat = db.Column(db.Float, nullable=False, default=100)
    last_produce = db.Column(db.Float, default=None)

    def set_time(self):
        self.last_produce = time()

    def produce(self):
        for building in self.buildings:
            building.produce()
        self.last_produce = time()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __str__(self):
        return self.username


class Building(db.Model):
    __tablename__ = "Building"
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, nullable=False, default=0)
    upgrade_gold = db.Column(db.Integer, nullable=False, default=50)
    upgrade_meat = db.Column(db.Integer, nullable=False, default=25)
    production_speed = db.Column(db.Integer, nullable=False, default=0)
    building_type = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.ForeignKey('User.id'))
    user = db.relationship('User', back_populates='buildings')
    __mapper_args__ = {'polymorphic_on': building_type, 'polymorphic_identity': 'Building'}

    def _production_speed(self):
        return 0

    def upgrade(self):
        if self.user.gold >= self.upgrade_gold and self.user.meat >= self.upgrade_meat:
            self.user.gold -= self.upgrade_gold
            self.user.meat -= self.upgrade_meat
            self.level += 1
            self.upgrade_gold = self.upgrade_gold*10
            self.upgrade_meat = self.upgrade_meat*10
            self.production_speed = self._production_speed()
            return True
        else:
            return False

    def produce(self): pass


class GoldBuilding(Building):
    __mapper_args__ = {'polymorphic_identity': 'gold'}
    base_production_speed = 4

    def set_production_speed(self):
        self.production_speed = self._production_speed()

    def _production_speed(self):
        return self.base_production_speed ** self.level

    def produce(self):
        self.user.gold += self._production_speed()*(time() - self.user.last_produce)


class MeatBuilding(Building):
    __mapper_args__ = {'polymorphic_identity': 'meat'}
    base_production_speed = 5

    def set_production_speed(self):
        self.production_speed = self._production_speed()

    def _production_speed(self):
        return self.base_production_speed ** self.level

    def produce(self):
        self.user.meat += self._production_speed()*(time() - self.user.last_produce)


class Barracks(db.Model):
    __table_name__ = 'Barracks'
    id = db.Column(db.Integer, primary_key=True)
