from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


#nicio do Models

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db = SQLAlchemy(app)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Lembrar-me')
    submit = SubmitField('Log In')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    available = db.Column(db.Boolean, nullable=False, default=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)

class RegisterForm(FlaskForm):
    username = StringField('Nome de usuário')
    password = PasswordField('Senha')
    confirm_password = PasswordField('Confirmar senha')
    submit = SubmitField('Registrar')

class sub_menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Define a função de carregamento do usuário
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_app():
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

with app.app_context():
    db.create_all()

#Fim do Models

#Inicio das Rotas
@app.route('/')
@app.route('/home')
def index():
    restaurants = Restaurant.query.all()
    if not restaurants:
        return 'Nenhum restaurante encontrado.'
    menu_items = Dish.query.all()
    if not menu_items:
        return 'Nenhum item de menu encontrado.'
    return render_template('index.html', restaurant=restaurants[0], menu_items=menu_items)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login inválido')

    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        if password != confirm_password:
            flash('As senhas não conferem.')
            return render_template('register.html', form=form)
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

#Fim de Rotas

if __name__ == '__main__':
    init_app()
    app.run(debug=True)

