from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Создаем таблицы
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('profile'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Если пользователь уже авторизован, перенаправляем на профиль
    if 'user_id' in session:
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # Сохраняем данные пользователя в сессии
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'Добро пожаловать, {username}!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Неверный логин или пароль', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/profile')
def profile():
    # Проверяем, авторизован ли пользователь
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в систему', 'error')
        return redirect(url_for('login'))
    
    return render_template('profile.html', username=session.get('username'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Если пользователь уже авторизован, перенаправляем на профиль
    if 'user_id' in session:
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        captcha = request.form.get('captcha')
        
        # Проверка капчи (checkbox)
        if not captcha:
            flash('Пожалуйста, подтвердите, что вы не робот', 'error')
            return render_template('register.html')
        
        # Проверка совпадения паролей
        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return render_template('register.html')
        
        # Проверка длины пароля
        if len(password) < 6:
            flash('Пароль должен содержать минимум 6 символов', 'error')
            return render_template('register.html')
        
        # Проверка, существует ли пользователь
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Пользователь с таким именем уже существует', 'error')
            return render_template('register.html')
        
        # Создание нового пользователя
        new_user = User(username=username)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Регистрация успешна! Теперь вы можете войти', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    # Очищаем сессию
    session.clear()
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)