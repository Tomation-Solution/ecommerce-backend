from flask_mail import Message
from config import mail
# mail sender app
def send_mail(title,recipient,body=None, email=None, password=None):
    msg = Message(title, recipients=[recipient])
    if body == None:
        msg.html = """
        <h2>welcome to Our e-commerce platform</h2>
        <p>your username is {} and password is {}</p>
        For more enquiry feel free to contact us
    """.format(email,password)
    else:
        msg.body = body
    mail.send(msg)

def sales_view_table_updater(product, sales=False, views=True):
    if views:
        pass
    elif sales:
        pass
ALLOWED_EXTENSIONS = {'jpg','png','jpeg','gif'}
    
