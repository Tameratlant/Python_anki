from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cards.db'
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Измените на реальный секретный ключ

db = SQLAlchemy(app)

# Модель карточки
class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    front_text = db.Column(db.String(100), nullable=False)
    back_text = db.Column(db.String(100), nullable=False)
    tag = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(20), nullable=False)
    correct_answers = db.Column(db.Integer, default=0)
    wrong_answers = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_reviewed = db.Column(db.DateTime)

# Форма для добавления карточки
class AddCardForm(FlaskForm):
    front_text = StringField('Загаданное слово', validators=[DataRequired()])
    back_text = StringField('Ответ', validators=[DataRequired()])
    tag = StringField('Тег', validators=[DataRequired()])
    color = SelectField('Цвет карточки', choices=[
        ('red', 'Красный'),
        ('blue', 'Синий'),
        ('green', 'Зелёный'),
        ('yellow', 'Жёлтый')
    ], validators=[DataRequired()])
    submit = SubmitField('Добавить карточку')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_cards', methods=['GET', 'POST'])
def add_cards():
    form = AddCardForm()
    if form.validate_on_submit():
        new_card = Card(
            front_text=form.front_text.data,
            back_text=form.back_text.data,
            tag=form.tag.data,
            color=form.color.data
        )
        db.session.add(new_card)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_card.html', form=form)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создаём таблицы в БД
    app.run(debug=True)

class AddCardForm(FlaskForm):
    front_text = StringField('Загаданное слово', validators=[DataRequired()], render_kw={"placeholder": "Введите загаданное слово"})
    back_text = StringField('Ответ', validators=[DataRequired()], render_kw={"placeholder": "Введите правильный ответ"})
    tag = StringField('Тег', validators=[DataRequired()], render_kw={"placeholder": "Например: 'глаголы', 'еда'"})
    color = SelectField('Цвет карточки', choices=[
        ('red', 'Красный'),
        ('blue', 'Синий'),
        ('green', 'Зелёный'),
        ('yellow', 'Жёлтый')
    ], default='red', validators=[DataRequired()])
    submit = SubmitField('Добавить карточку')