from flask import flash
from Manager import UseDataBase
import mysql.connector
from datetime import datetime


'''Delete account'''

def delete_account(email: str, config: dict, value: str) -> bool:
    
    try:
        if value == 'yes':
            with UseDataBase(config) as cursor:
                sql = "delete from upi WHERE email = %s"
                cursor.execute(sql, (email, ) )
            
            return True
        else:
            return False

    except mysql.connector.errors.ProgrammingError as err:
        print('MySQL Programing. Error form **delete_account**', err)
    except Exception as exErr:
        print('Error form **delete_account**', exErr)
        flash('Sorry in this moment we are out of service try later.', category='info')
        return False


'''Reset the week hours and minutes'''

def reset_week_hour_minute(email: str, config: dict) -> None:
    try:
        with UseDataBase(config) as cursor:
            sql = "select deadline_w_number, year, l_w_hour, l_w_min, c_w_hour, c_w_min from upi WHERE email = %s"
            cursor.execute(sql, (email, ) )
            contents = cursor.fetchone()
            
            weekNumber = contents[0]
            year = contents[1]

            # Update the hours and minutes from last and current week
            l_w_hour = contents[2]
            l_w_min = contents[3]
            c_w_hour = 0
            c_w_min = 0

            newWeekNumber = datetime.today().isocalendar().week
            newYear =datetime.today().isocalendar().year

            if weekNumber < newWeekNumber:
                sql = "update upi set deadline_w_number = %s, year = %s, l_w_hour = %s, l_w_min = %s, c_w_hour = %s, c_w_min = %s WHERE email = %s"
                cursor.execute(sql, (newWeekNumber, newYear, l_w_hour, l_w_min, c_w_hour, c_w_min, email, ) )
            else:
                if year < newYear and weekNumber > newWeekNumber:
                    sql = "update upi set deadline_w_number = %s, year = %s, l_w_hour = %s, l_w_min = %s, c_w_hour = %s, c_w_min = %s WHERE email = %s"
                    cursor.execute(sql, (newWeekNumber, newYear, l_w_hour, l_w_min, c_w_hour, c_w_min, email, ) )
    except mysql.connector.errors.ProgrammingError as err:
        print('MySQL Programing. Error from **reset_week_hour_minute**', err)
        




'''Get user's name '''

def get_user_name(email: str, config: dict) -> str:
    try:
        with UseDataBase(config) as cursor:
            sql = "select name from upi WHERE email = %s"
            cursor.execute(sql, (email, ) )
            name = cursor.fetchone()

        return str(name[0])
    except mysql.connector.errors.ProgrammingError as err:
        print('MySQL Programing. Error from **get_user_name**', err)
        return ''



'''Udate current week hours and minutes'''

def Update_C_W_Hrs(args) -> None:
    hour = args[0]
    minute = args[1]
    c_w_hour = args[2]
    c_w_min = args[3]

    c_w_hour = c_w_hour + hour
    c_w_min = c_w_min + minute

    if c_w_min >= 60:
        args[2] = c_w_hour + 1
        args[3] = c_w_min - 60 # This just adjust the new minutes
    else:
        args[2] = c_w_hour
        args[3] = c_w_min



'''Update the just the hours and minutes when user subtract hours'''

def update_subtracted_hour(hour: int, minute: int, config: dict, email: str) -> None:

    try:
        with UseDataBase(config) as cursor:
            sql = "update upi set t_hour = %s, t_min = %s WHERE email = %s"
            cursor.execute(sql, (hour, minute, email, ) )
    except mysql.connector.errors.ProgrammingError as err:
        print('MySQL Programming, Error from **update_subtracted_hour**', err)



'''Update Datebase'''

def UpdateDB(args: tuple, config: dict,  email: str, totalHour: str = 'totalHour') -> None:

    if totalHour == 'totalHour':
        
        with UseDataBase(config) as cursor:
            sql = "UPDATE upi SET t_hour = %s, t_min = %s, c_w_hour = %s, c_w_min = %s WHERE email = %s "
            
            cursor.execute(sql, (args[0], args[1], args[2], args[3], email, ) )
    
    else:
        with UseDataBase(config) as cursor:
            sql = "UPDATE upi SET c_w_hour = %s, c_w_min = %s, l_w_hour = %s, l_w_min = %s WHERE email = %s "
            
            cursor.execute(sql, (args[0], args[1], args[2], args[3], args[4], ) )



'''Add hours'''

def add_hours(hour: int, minute: int, config: dict, email: str) -> bool:

    res = False
    
    # Negative hours or minutes are not valide
    if hour < 0 or minute < 0:
        flash('Hours and minutes can not be negative', category='error')
        return res
    

    # Minutes and hours must be of type int
    if type(hour) == int and type(minute) == int:

        # Minute must be in this range
        if minute >= 0 and minute <= 60:

            #Get the current hours and minutes
            try:
                with UseDataBase(config) as cursor:
                    cursor.execute("select t_hour, t_min, c_w_hour, c_w_min from upi WHERE email = %s", (email, ) )
                    contents = cursor.fetchone()
    
                hr = contents[0]
                mn = contents[1]

                newHour = hr + hour
                newMin = mn + minute
            
            except mysql.connector.ProgrammingError as err:
                print('MySQL Programming. Error from **add_hours**', err)
            except Exception as exErr:
                print('Error from **add_hours**', exErr)
                return res

            if newMin >= 60:
                newHour += 1
                newMin = newMin - 60 # This just adjust the new minutes

                '''Here update c_w_hour, c_w_min and database check
                   that the hour and minutes that are passed into 
                   list are the user input'''

                newList = [hour, minute, contents[2], contents[3]]
                Update_C_W_Hrs(newList)

                try:

                    # So here make sure to give the new hours and minutes
                    Temp = [newHour, newMin, newList[2], newList[3]]
                    UpdateDB(tuple(Temp), config, email)

                except mysql.connector.errors.ProgrammingError as err:
                    print('MySQL Programming', err)
                except Exception as exErr:
                    print('Error from **add_hours**', exErr)
                    return res
                    
                
                flash('Your submit was successfully complited!', category='info')
                res = True # Update the bool value
                return res 
            else:
                
                '''Here update c_w_hour, c_w_min and database check
                   that the hour and minutes that are passed into 
                   list are the user input'''
                
                newList = [hour, minute, contents[2], contents[3]]

                Update_C_W_Hrs(newList)

                try:

                    # So here make sure to give the new hours and minutes
                    Temp = [newHour, newMin, newList[2], newList[3]]
                    UpdateDB(tuple(Temp), config, email)

                except mysql.connector.errors.ProgrammingError as err:
                    print('MySQL Programming', err)
                except Exception as exErr:
                    print('Error from **add_hours**', exErr)
                    return res
                
                flash('Your submit was successfully completed!', category='info')

                res = True
                return res
        else:
            flash('Hours and minutes must be in range of 0 and 60', category='error')
            return res
    else:
        flash('Hours and minutes must be integer', category='error')
        return res
    



'''Subtract hours'''

def Subtract_hours(hour: int, minute: int, config: dict, email: str) -> bool:
    
    res = False

    # Negative hours or minutes are not valide
    if hour < 0 or minute < 0:
        flash('Hours and minutes can not be negative', category='error')
        return res
    

    # Minutes and hours must be of type int
    if type(hour) == int and type(minute) == int:

        # Minute must be in this range
        if minute >= 0 and minute <= 60:
            
            try:
                with UseDataBase(config) as cursor:
                    cursor.execute("select t_hour, t_min, c_w_hour, c_w_min from upi WHERE email = %s", (email, ) )
                    contents = cursor.fetchone()
    
                hr = contents[0]
                mn = contents[1]

                '''Check if the hour to subtract is smaller than the current hour'''
                if hour > hr:
                    flash('You dont have enough Hours to subtract', category='error')
                    return res

                if hr == 0:
                    if hr == hour and minute > mn:
                        flash('You dont have enough Minetus to subtract', category='error')
                        return res

                newHour = hr - hour
                newMin = mn - minute

                
                if newHour > 0:
                    if newMin < 0:
                        newHour -= 1
                        newMin = 60 + newMin
                        update_subtracted_hour(newHour, newMin, config, email)
                        flash('Your submit was successfully completed!', category='info')
                        res = True
                        return res
                    else:
                        update_subtracted_hour(newHour, newMin, config, email)
                        flash('Your submit was successfully completed!', category='info')
                        res = True
                        return res
                else:
                    '''The current hours never won be smaller than the hours to suctract'''
                    if newHour == 0:
                        if newMin >= 0:
                            update_subtracted_hour(newHour, newMin, config, email)
                            flash('Your submit was successfully completed!', category='info')
                            res = True
                            return res
                        else:
                            flash('You dont have enough Minetus to subtract', category='error')
                            return res
            except mysql.connector.ProgrammingError as err:
                print('MySQL Programming', err)
            except Exception as exErr:
                flash('Sorry in this moment we are out of service try later.', category='info')
                print('Error from **subtract_hours**', exErr)
                return res
        else:
            flash('Hours and minutes must be in range of 0 and 60', category='error')
            return res
    else:
        flash('Hours and minutes must be integer', category='error')
        return res




'''Check if email or password already exist or not'''

def email_password_exit(email, config: dict) -> bool:

    #Later handle exception here
    try:
        with UseDataBase(config) as cursor:
            cursor.execute("select email from upi WHERE email= %s ", (email,))
            contents = cursor.fetchone()
        
        if contents:
            return True
        else:
            return False
    
    except mysql.connector.errors.ProgrammingError as err:
        print('MySQL Programming', err)
    except Exception as exErr:
        print('Error from **email_password_exit**', exErr)
        return False



'''Analizes the data from sign up'''


def analize_signup_data(name: str, lastName: str, email: str, 
password1: str, password2: str, config: dict) -> bool:
    if len(name) < 4:
        flash('The name must have more than 3 chacacters', category='error')
        return False
        
    elif len(lastName) < 4:
        flash('The last name must have more than 3 chacacters', category='error')
        return False

    elif '@' not in email:
        flash('The email must have @ chacacter', category='error')
        return False

    elif '.' not in email:
        flash('The email must have ( . ) chacacter', category='error')
        return False

    elif len(password1) < 7:
        flash('The password must have more than 6 chacacters', category='error')
        return False

    elif password1 != password2:
        flash('Your passwords dont match', category='error')
        return False

    else:

        if not email_password_exit(email, config):

            try:
                #Insert the new user data to the database
                with UseDataBase(config) as cursor:
                    query = "insert into upi(name, last_name, email, password) values (%s, %s, %s, %s)"
                    cursor.execute(query, (name, lastName, email, password1,))

                flash('Your sign up was successfull', category='info')
                return True

            except mysql.connector.errors.ProgrammingError as err:
                print('MySQL Programming', err)
            except Exception as exErr:
                flash('Sorry in this moment we are out of service try later.', category='info')
                print('Error from **analize_signup_data**', exErr)
                return False

        else:
            flash('The email already exit', category='info')
            return False



'''Analize the sign in data'''

def analize_signin_data(email: str, password: str, config: dict) -> bool:
    
    #Check if the email exit
    try:
        with UseDataBase(config) as cursor:
            sql = "select password from upi WHERE email= %s"
            cursor.execute(sql, (email, ))
            contents = cursor.fetchone()
    
        if not contents:
            flash("The email does not exit", category='info')
            return False
        else:
            # Validate the password attached to email

            for x in contents:
                if x == password:
                    return True
        
        # Whenever the password could not be found
        flash("Your password is incorrect ", category='info')
        return False
    except mysql.connector.errors.ProgrammingError as err:
        print('MySQL Programing', err)
    except Exception as exErr:
        flash('Sorry in this moment we are out of service try later.', category='info')
        print('Error from **analize_signin_data**', exErr)
        return False

    

'''Get the data from an user'''
def get_view_data(email: str, config: dict) -> tuple:

    try:
        with UseDataBase(config) as cursor:
            sql = "select l_w_hour, l_w_min, c_w_hour, c_w_min, t_hour, t_min from upi WHERE email = %s"
            cursor.execute(sql, (email, ) )
            contents = cursor.fetchone()
        
        return contents
    except mysql.connector.errors.ProgrammingError as err:
        print('Mysql programing', err)
    except Exception as exErr:
        flash('Sorry in this moment we are out of service try later.', category='info')
        print('Error from **get_view_data**', exErr)
        return tuple()