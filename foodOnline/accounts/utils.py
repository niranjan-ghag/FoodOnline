def detectUser(user):
    if user.role == 1:
        redirect_url = 'vendordashboard'
    elif user.role == 0:
        redirect_url = 'custdashboard'
    else:
        redirect_url = '/admin'
    
    return redirect_url
