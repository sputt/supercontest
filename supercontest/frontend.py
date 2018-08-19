from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField


class PickForm(Form):
    name = TextField('Name:', validators=[validators.required()])
    pick = TextField('Pick:', validators=[validators.required()])

    def reset(self):
        blankData = MultiDict([('csrf', self.reset_csrf())])
        self.process(blankData)
