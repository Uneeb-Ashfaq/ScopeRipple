from app.db.database import check_connection


# Verify the Supabase database connection
def main():
    result = check_connection()

    if result == 1:
        print("SQLite connection successful!")


if __name__ == "__main__":
    main()