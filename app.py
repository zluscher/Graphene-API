# Imports
from flask import Flask
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from flask_sqlalchemy import SQLAlchemy
from flask_graphql import GraphQLView


# initializing our app
app = Flask(__name__)
app.debug = True

# Configs
# Our database configurations will go here

# Replace the user, password, hostname and database according to your configuration information

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/graphql'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


# Modules
# SQLAlchemy will be initiated here
db = SQLAlchemy(app)

# Models
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, index=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    books = db.relationship('Book', backref='author')

    def __init__(self, username, email):
      self.username = username
      self.email = email

    def __repr__(self):
        return '' % self.id

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), index=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '' % self.title % self.description % self.year % self.author_id

# mike = User(username='mikedean', email='mikedean@gmail.com')
# db.session.add(mike)
# db.session.commit()
# flaskbook = Book()
# flaskbook.title = "Building with Flask"
# flaskbook.description = "The best Flask Python book on the web"
# flaskbook.year = 2019
# flaskbook.author_id = mike.id
# db.session.add(flaskbook)
# db.session.commit()

# Our relations will be setup here

# Schema Objects
# Our schema objects will go here
class BookObject(SQLAlchemyObjectType):
   class Meta:
       model = Book
       interfaces = (graphene.relay.Node, )

class UserObject(SQLAlchemyObjectType):
   class Meta:
       model = User
       interfaces = (graphene.relay.Node, )

class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    all_books = SQLAlchemyConnectionField(BookObject)
    all_users = SQLAlchemyConnectionField(UserObject)

schema = graphene.Schema(query=Query)
class BookObject(SQLAlchemyObjectType):
   class Meta:
       model = Book
       interfaces = (graphene.relay.Node, )

class UserObject(SQLAlchemyObjectType):
   class Meta:
       model = User
       interfaces = (graphene.relay.Node, )

class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    all_books = SQLAlchemyConnectionField(BookObject)
    all_users = SQLAlchemyConnectionField(UserObject)

schema = graphene.Schema(query=Query)

class AddBook(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String(required=True)
        year = graphene.Int(required=True)
        username = graphene.String(required=True)
    book = graphene.Field(lambda: BookObject)

    def mutate(self, info, title, description, year, username):
        user = User.query.filter_by(username=username).first()
        book = Book(title=title, description=description, year=year)
        if user is not None:
            book.author = user
        db.session.add(book)
        db.session.commit()
        return AddBook(book=book)

class Mutation(graphene.ObjectType):
    add_book = AddBook.Field()
schema = graphene.Schema(query=Query, mutation=Mutation)

# Routes
# Our GraphQL route will go here

app.add_url_rule(
    '/graphql-api',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True # for having the GraphiQL interface
    )
)

@app.route('/')
def index():
    return 'Welcome to Book Store Api'
if __name__ == '__main__':
     app.run()
