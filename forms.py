from flaskext.wtf import Form, HiddenField, TextField, TextAreaField, PasswordField, Required, EqualTo
from datetime import datetime

class SettingsForm(Form):
    password = PasswordField()
    confirm = PasswordField(validators=[EqualTo('password',
                                                message='Password & confirmation must match')])
    email = TextField()


class SigninForm(Form):
    username = TextField(validators=[Required()])
    password = PasswordField(validators=[Required()])


class SignupForm(Form):
    username = TextField(validators=[Required()])
    password = PasswordField(validators=[Required(),
                                         EqualTo('confirm', message='Password & confirmation must match')])
    confirm = PasswordField()


class ScratchpadForm(Form):
    scratchpad = TextAreaField()
