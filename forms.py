from flaskext.wtf import Form, HiddenField, TextField, TextAreaField, PasswordField, Required, EqualTo
from datetime import datetime

class EntryForm(Form):
    entry_id = HiddenField(default=datetime.now().strftime("%Y%m%d.01"))
    body = TextAreaField(validators=[Required()])

class SigninForm(Form):
    username = TextField(validators=[Required()])
    password = PasswordField(validators=[Required()])

class SignupForm(Form):
    username = TextField(validators=[Required()])
    password = PasswordField(validators=[Required(),
                                         EqualTo('confirm', message='Password & confirmation must match')])
    confirm = PasswordField()
    invitation_code = TextField(validators=[Required()])
