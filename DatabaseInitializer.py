import psycopg2

class DatabaseInitializer:

    def __init__(self, connection):
        self.connection = connection

    def initialize_login_info(self):
        cursor = self.connection.cursor()

        # initialize the LoginInfo table
        try:
            cursor.execute("SELECT * From LoginInfo LIMIT 1")
        except psycopg2.ProgrammingError.UndefinedTable:
            self.connection.rollback()
            cursor.execute("""CREATE TABLE LoginInfo (
                    username varchar(20) NOT NULL PRIMARY KEY, 
                    password varchar(25) NOT NULL, 
                    usertype varchar(20))""")
            self.connection.commit()

    def initialize_customers(self):
        cursor = self.connection.cursor()
        # initialize the Customer table
        try:
            cursor.execute("SELECT * From Customers LIMIT 1")
        except psycopg2.ProgrammingError.UndefinedTable:
            self.connection.rollback()
            cursor.execute("""CREATE TABLE Customers (
                    username varchar(20) REFERENCES LoginInfo(username), 
                    name varchar(255),
                    bankInformation varchar(25) not null, 
                    address varchar(255), 
                    contact varchar(255))""")
            self.connection.commit()

    def initialize_drivers(self):
        cursor = self.connection.cursor()
        # initialize the Drivers table
        try:
            cursor.execute("SELECT * From Drivers LIMIT 1")
        except psycopg2.ProgrammingError.UndefinedTable:
            self.connection.rollback()
            cursor.execute("""CREATE TABLE Drivers (
                    username varchar(20) REFERENCES LoginInfo(username), 
                    name varchar(255), 
                    contact varchar(255))""")
            self.connection.commit()

    def initialize_suppliers(self):
        cursor = self.connection.cursor()

        # initialize the Supplier table
        try:
            cursor.execute("SELECT * From Suppliers LIMIT 1")
        except psycopg2.ProgrammingError.UndefinedTable:
            self.connection.rollback()
            cursor.execute("""CREATE TABLE Suppliers (
                    username varchar(20) REFERENCES LoginInfo(username), 
                    name varchar(255) not null,
                    bankInformation varchar(255) not null,
                    contact varchar(255) not null)""")
            self.connection.commit()

    def initialize_invoices(self):
        cursor = self.connection.cursor()

        # initialize the Supplier table
        try:
            cursor.execute("SELECT * From Invoices LIMIT 1")
        except psycopg2.ProgrammingError.UndefinedTable:
            self.connection.rollback()
            cursor.execute("""CREATE TABLE Invoices (
                    invoiceID INT GENERATED BY DEFAULT AS IDENTITY,
                    customerUsername varchar(255) references Customers(username) not null,
                    supplierUsername varchar(255) references Suppliers(username) not null,
                    driverUsername varchar(255) references Drivers(username), 
                    issuedDate date,
                    completionDate date,
                    onTheWay boolean, 
                    arrived boolean,
                    payment boolean
                    )""")
            self.connection.commit()

    def initialize_orders(self):
        cursor = self.connection.cursor()
        try:
            cursor.exectue("SELECT * FROM Orders LIMIT 1")
        except:
            self.connection.rollback()
            cursor.exectue("""CREATE TABLE Items (
                    item varchar(255),
                    price FLOAT,
                    amount INT,
                    invoiceID int references Invoices(invoiceID)
                    """)

    def initialize(self):
        self.initialize_login_info()
        self.initialize_customers()
        self.initialize_drivers()
        self.initialize_suppliers()
        self.initialize_invoices()
        self.initialize_orders()


