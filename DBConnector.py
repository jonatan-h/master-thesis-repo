import mysql.connector
from mysql.connector import Error
import main


def create_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print("The error {} occurred".format(e))
    return connection


def execute_query(connection, query, query_type, print_flag):
    cursor = connection.cursor(buffered=True)
    try:
        for result in cursor.execute(query, multi=True):
            if print_flag:
                if result.with_rows:
                    print("Rows produced by query '{}'".format(result.statement))
                    print(result.fetchall())
                else:
                    print("Number of rows affected by statement '{}': {}".format(
                        result.statement, result.rowcount))
        connection.commit()
        if print_flag:
            print("{} executed successfully".format(query_type))
    except Error as e:
        print("The error {} occurred for {}".format(e, query_type))


def use(connection, database_name, print_flag):
    """Specifies which database to use, if there are multiple"""
    query = """USE {}""".format(database_name)
    execute_query(connection, query, "USE", print_flag)


def show_databases(connection, print_flag):
    """Lists all the available databases"""
    query = """SHOW DATABASES"""
    execute_query(connection, query, "SHOW DATABASES", print_flag)


def show_tables(connection, print_flag):
    """Lists all the tables inside a database"""
    query = """SHOW TABLES"""
    execute_query(connection, query, "SHOW TABLES", print_flag)


def describe(connection, table_name, print_flag):
    query = """DESCRIBE {}""".format(table_name)
    execute_query(connection, query, "DESCRIBE", print_flag)


def insert_into(connection, db_table, db_entry, print_flag):
    """Insert db_entry into database table db_table"""

    if "model" in db_entry:
        query = """INSERT INTO {} (model) VALUES ('{}')""".format(db_table, db_entry["model"])
        execute_query(connection, query, "INSERT INTO", print_flag)
    if "size" in db_entry:
        query = """INSERT INTO {} (size) VALUES ('{}')""".format(db_table, db_entry["size"])
        execute_query(connection, query, "INSERT INTO", print_flag)
    if "headform" in db_entry:
        query = """INSERT INTO {} (headform) VALUES ('{}')""".format(db_table, db_entry["headform"])
        execute_query(connection, query, "INSERT INTO", print_flag)
    if "helmet_type" in db_entry:
        query = """INSERT INTO {} (helmet_type) VALUES ('{}')""".format(db_table, db_entry["helmet_type"])
        execute_query(connection, query, "INSERT INTO", print_flag)
    if "epp_density" in db_entry:
        query = """INSERT INTO {} (epp_density) VALUES ('{}')""".format(db_table, db_entry["epp_density"])
        execute_query(connection, query, "INSERT INTO", print_flag)
    if "eps_density" in db_entry:
        query = """INSERT INTO {} (eps_density) VALUES ('{}')""".format(db_table, db_entry["eps_density"])
        execute_query(connection, query, "INSERT INTO", print_flag)
    if "test_type" in db_entry:
        query = """INSERT INTO {} (test_type) VALUES ('{}')""".format(db_table, db_entry["test_type"])
        execute_query(connection, query, "INSERT INTO", print_flag)
    if "test_condition" in db_entry:
        query = """INSERT INTO {} (test_condition) VALUES ('{}')""".format(db_table, db_entry["test_condition"])
        execute_query(connection, query, "INSERT INTO", print_flag)
    if "anvil" in db_entry:
        query = """INSERT INTO {} (anvil) VALUES ('{}')""".format(db_table, db_entry["anvil"])
        execute_query(connection, query, "INSERT INTO", print_flag)
    if "impact_location" in db_entry:
        query = """INSERT INTO {} (impact_location) VALUES ('{}')""".format(db_table, db_entry["impact_location"])
        execute_query(connection, query, "INSERT INTO", print_flag)
    if "peak" in db_entry:
        query = """INSERT INTO {} (peak) VALUES ('{}')""".format(db_table, db_entry["peak"])
        execute_query(connection, query, "INSERT INTO", print_flag)
    if "criteria" in db_entry:
        query = """INSERT INTO {} (criteria) VALUES ('{}')""".format(db_table, db_entry["criteria"])
        execute_query(connection, query, "INSERT INTO", print_flag)
    if "safety_factor" in db_entry:
        query = """INSERT INTO {} (safety_factor) VALUES ('{}')""".format(db_table, db_entry["safety_factor"])
        execute_query(connection, query, "INSERT INTO", print_flag)
    if "result" in db_entry:
        query = """INSERT INTO {} (result) VALUES ('{}')""".format(db_table, db_entry["result"])
        execute_query(connection, query, "INSERT INTO", print_flag)
    if "stage_of_testing" in db_entry:
        query = """INSERT INTO {} (stage_of_testing) VALUES ('{}')""".format(db_table, db_entry["stage_of_testing"])
        execute_query(connection, query, "INSERT INTO", print_flag)

    # query = """INSERT INTO {} (
    # model,
    # size,
    # headform,
    # helmet_type,
    # epp_density,
    # eps_density,
    # test_type,
    # test_condition,
    # anvil,
    # impact_location,
    # peak,
    # criteria,
    # safety_factor,
    # result,
    # stage_of_testing) VALUES
    # ('{}', '{}',
    # '{}', '{}', '{}',
    # '{}', '{}', '{}',
    # '{}', '{}', {},
    # {}, {}, '{}',
    # '{}')""".format(
    #                     db_table,
    #                     db_entry["model"] if "model" in db_entry else "",
    #                     db_entry["size"] if "size" in db_entry else "",
    #                     db_entry["headform"] if "headform" in db_entry else "",
    #                     db_entry["helmet_type"] if "helmet_type" in db_entry else "",
    #                     db_entry["epp_density"] if "epp_density" in db_entry else "",
    #                     db_entry["eps_density"] if "eps_density" in db_entry else "",
    #                     db_entry["test_type"] if "test_type" in db_entry else "",
    #                     db_entry["test_condition"] if "test_condition" in db_entry else "",
    #                     db_entry["anvil"] if "anvil" in db_entry else "",
    #                     db_entry["impact_location"] if "impact_location" in db_entry else "",
    #                     db_entry["peak"] if "peak" in db_entry else "",
    #                     db_entry["criteria"] if "criteria" in db_entry else "",
    #                     db_entry["safety_factor"] if "safety_factor" in db_entry else "",
    #                     db_entry["result"] if "result" in db_entry else "",
    #                     db_entry["stage_of_testing"] if "stage_of_testing" in db_entry else "",
    # )
    #
    # execute_query(connection, query, "INSERT INTO", print_flag)


def select_all(connection, db_table, print_flag):
    """Get all entries from a database table"""
    query = """SELECT * FROM {}""".format(db_table)
    execute_query(connection, query, "SELECT *", print_flag)


def select_column(connection, db_table, column, print_flag):
    """Get all values of certain column in database table db_table"""
    query = """SELECT {} FROM {}""".format(column, db_table)
    execute_query(connection, query, "SELECT {}".format(column), print_flag)


def delete_all(connection, db_table, print_flag):
    """Delete all entries in database table db_table"""
    query = """DELETE FROM {}""".format(db_table)
    execute_query(connection, query, "DELETE FROM", print_flag)
