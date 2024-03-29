from src import db
from time import time
from sqlalchemy.ext.hybrid import hybrid_property


class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    buildings = db.relationship('Building', back_populates="user")
    gold = db.Column(db.Float, nullable=False, default=100)
    meat = db.Column(db.Float, nullable=False, default=100)
    swordsman = db.Column(db.Integer, nullable=False, default=0)
    last_produce = db.Column(db.Float, default=None)
    win = db.Column(db.Integer, nullable=False, default=1)
    lose = db.Column(db.Integer, nullable=False, default=1)

    def set_time(self):
        self.last_produce = time()

    def produce(self):
        for building in self.buildings:
            if isinstance(building, ResourceBuilding):
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

    def score(self):
        return ((self.win / self.lose) * (self.win / self.lose)) * sum([building.level for building in self.buildings]) / len(self.buildings) * (self.swordsman + 1)

    def __str__(self):
        return self.username


class Building(db.Model):
    __tablename__ = "Building"
    base_upgrade_gold = 5
    base_upgrade_meat = 2
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, nullable=False, default=0)
    building_type = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.ForeignKey('User.id'))
    user = db.relationship('User', back_populates='buildings')
    __mapper_args__ = {'polymorphic_on': building_type, 'polymorphic_identity': 'Building'}

    def upgrade_gold(self):
        return self.base_upgrade_gold * (3 ** self.level)

    def upgrade_meat(self):
        return self.base_upgrade_meat * (3 ** self.level)

    def upgrade(self):
        upgrade_gold = self.upgrade_gold()
        upgrade_meat = self.upgrade_meat()
        if self.user.gold >= upgrade_gold and self.user.meat >= upgrade_meat:
            self.user.gold -= upgrade_gold
            self.user.meat -= upgrade_meat
            self.level += 1
            return True
        else:
            return False


class ResourceBuilding(Building):

    def resource(self): pass

    def get_production_speed(self):
        return self.base_production_speed ** self.level * ((self.level / 10) + 2)

    def produce(self): pass


class GoldBuilding(ResourceBuilding):
    __mapper_args__ = {'polymorphic_identity': 'gold'}
    base_production_speed = 1.4
    img = "/static/img/goldmine.png"

    @hybrid_property
    def resource(self):
        return self.user.gold

    def produce(self):
        self.user.gold += self.get_production_speed() * (time() - self.user.last_produce)


class MeatBuilding(ResourceBuilding):
    __mapper_args__ = {'polymorphic_identity': 'meat'}
    base_production_speed = 1.5
    img = "/static/img/barnyard.png"

    @hybrid_property
    def resource(self):
        return self.user.meat

    def produce(self):
        self.user.meat += self.get_production_speed() * (time() - self.user.last_produce)


class SoldierBuilding(Building):

    def produce(self, count): pass


class SwordsmanBuilding(SoldierBuilding):
    __mapper_args__ = {'polymorphic_identity': 'swordsman'}
    base_gold_cost = 20
    base_meat_cost = 30
    base_upgrade_gold = 15
    base_upgrade_meat = 12
    cost_reducement_multiplier = 1.2
    img = "/static/img/armytower.png"

    def meat_cost(self):
        return int(self.base_meat_cost / (self.cost_reducement_multiplier ** self.level))

    def gold_cost(self):
        return int(self.base_gold_cost / (self.cost_reducement_multiplier ** self.level))

    def produce(self, count):
        required_gold = self.gold_cost() * count
        required_meat = self.meat_cost() * count
        if (self.user.gold >= self.gold_cost() * count) and (self.user.meat >= self.meat_cost() * count):
            self.user.swordsman += count
            self.user.gold -= required_gold
            self.user.meat -= required_meat
            return True
        return False

    def count(self):
        return self.user.swordsman
