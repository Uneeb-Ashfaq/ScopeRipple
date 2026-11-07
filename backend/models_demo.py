
from app.db.models import Base


# Display the database tables defined in our models
def main():

    print("ScopeRipple Database Tables:")

    for table_name in Base.metadata.tables:
        print(table_name)


if __name__ == "__main__":
    main()
