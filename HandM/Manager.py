import mysql.connector

#This class inherits from Exception, and is an empty class

class ConnectionError(Exception):
    pass


class UseDataBase:

    #This is a constructor
    def __init__(self, config: dict) -> None:
        self.configuration = config

    def __enter__(self) -> 'cursor':

        try:
            self.conn = mysql.connector.connect(**self.configuration)
            self.cursor = self.conn.cursor()
            return self.cursor
        
        #Here use mysql error and my connection error
        except mysql.connector.errors.InterfaceError as err:
            raise ConnectionError(err)
        

    # The last 3 argument i have to know more about them
    def __exit__(self, exc_type, exc_value, exc_trace) -> None:

        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        