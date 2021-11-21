from flask import session, render_template

from functools import wraps

def check_login( fun ):
    @wraps(fun)

    def Wrapper_funtion(*args, **kwargs):
        if 'log_in' in session:
            return fun(*args, **kwargs)
        else:
            return render_template('decorator.html')

    
    return Wrapper_funtion