#we define a data model for our database

class User(BaseModel):
    id: int  # Add an ID field for the primary key
    username: str
    password: str