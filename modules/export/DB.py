import DBConnector


def store(connection, row):
    DBConnector.insert_into(connection, "test_suite", row, False)
