from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cards.db'
app.config['SECRET_KEY'] = 'your-secret-key-here'

db = SQLAlchemy(app)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    front_text = db.Column(db.String(100), nullable=False)
    back_text = db.Column(db.String(100), nullable=False)
    tag = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(20), nullable=False)
    correct_answers = db.Column(db.Integer, default=0)
    wrong_answers = db.Column(db.Integer, default=0)
    last_wrong_answer = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_reviewed = db.Column(db.DateTime)

# Форма для добавления карточки
class AddCardForm(FlaskForm):
    front_text = StringField('Загаданное слово', 
                           validators=[DataRequired()],
                           render_kw={"placeholder": "Введите загаданное слово"})
    back_text = StringField('Ответ',
                          validators=[DataRequired()],
                          render_kw={"placeholder": "Введите правильный ответ"})
    tag = StringField('Тег',
                     validators=[DataRequired()],
                     render_kw={"placeholder": "Например: 'глаголы', 'еда'"})
    color = SelectField('Цвет карточки', 
                       choices=[
                           ('red', 'Красный'),
                           ('blue', 'Синий'),
                           ('green', 'Зелёный'),
                           ('yellow', 'Жёлтый')
                       ], 
                       default='red',
                       validators=[DataRequired()])
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
        
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'success': True})
        
        flash('Карточка успешно добавлена!', 'success')
        return redirect(url_for('add_cards'))
    
    return render_template('add_card.html', form=form)

@app.route('/my_cards')
def my_cards():
    cards = Card.query.order_by(Card.created_at.desc()).all()
    return render_template('my_cards.html', cards=cards)

@app.route('/guess_by_tags')
def guess_by_tags():
    tags = db.session.query(Card.tag.distinct()).all()
    tags = [tag[0] for tag in tags]
    return render_template('guess_by_tags.html', tags=tags)

@app.route('/edit_card/<int:card_id>', methods=['GET', 'POST'])
def edit_card(card_id):
    card = Card.query.get_or_404(card_id)
    form = AddCardForm(obj=card)
    
    if form.validate_on_submit():
        form.populate_obj(card)
        db.session.commit()
        return redirect(url_for('my_cards'))
    
    return render_template('edit_card.html', form=form, card_id=card_id)

@app.route('/delete_card/<int:card_id>', methods=['POST'])
def delete_card(card_id):
    card = Card.query.get_or_404(card_id)
    db.session.delete(card)
    db.session.commit()
    return redirect(url_for('my_cards'))

@app.route('/guess_all')
def guess_all():
    # Получаем все карточки
    cards = Card.query.all()
    if not cards:
        return render_template('guess_all.html', card=None)
    card = random.choice(cards)  
    return render_template('guess_all.html', card=card)

@app.route('/handle_answer/<int:card_id>', methods=['POST'])
def handle_answer(card_id):
    card = Card.query.get_or_404(card_id)
    is_correct = request.form.get('is_correct') == 'true'
    next_page = request.form.get('next', 'guess_all')
    
    if is_correct:
        card.correct_answers += 1
    else:
        card.wrong_answers += 1
        card.last_wrong_answer = datetime.utcnow()  # Запоминаем время последнего неправильного ответа
    
    card.last_reviewed = datetime.utcnow()
    db.session.commit()
    return redirect(url_for(next_page))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создаём таблицы в БД
    app.run(debug=True)