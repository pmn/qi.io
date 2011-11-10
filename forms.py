from flaskext.wtf import Form, TextField, TextAreaField, PasswordField, Required, EqualTo

class EntryForm(Form):
    title = TextField(validators=[])
    body = TextAreaField(validators=[Required()])

class SigninForm(Form):
    username = TextField(validators=[Required()])
    password = PasswordField(validators=[Required()])

class SignupForm(Form):
    username = TextField(validators=[Required()])
    password = PasswordField(validators=[Required(),
                                         EqualTo('confirm', message='Password & confirmation must match')])
    confirm = PasswordField()
