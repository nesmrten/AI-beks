from app import db

# create a MetaData object
metadata = db.MetaData()

# reflect the tables in the database
metadata.reflect(bind=db.engine)

# get the names of the tables
table_names = metadata.tables.keys()

print(table_names)