from flask_wtf import FlaskForm
from wtforms import RadioField,SubmitField,StringField,FileField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from .. import photos

class imgs_classi(FlaskForm):
    imgs_classi_tuple=RadioField('开阔',choices=[('1','林荫'),('2','窄建'),('3','窄木'),('4','宽建'),('5','宽木'),('6','阔建'),('7','阔木'),('8','开阔')])
    submit=SubmitField('提交')

class upload_img(FlaskForm):
    photo=FileField(validators=[FileAllowed(photos, 'Image only!'), FileRequired('File was empty!')])
    submit=SubmitField('Upload')
