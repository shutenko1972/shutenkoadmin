from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
import logging
import os
from collections import OrderedDict

# --- Эта строка изменена для проверки ---
print("="*60)
print("Запущена версия 0.0.1")
print("="*60)
# ------------------------------------------

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, instance_relative_config=True)

# Указываем, что шаблоны находятся в корневой директории
app.template_folder = '.'

# Конфигурация базы данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Конфигурация Swagger с улучшенной поддержкой динамических маршрутов
app.config['SWAGGER'] = {
    'title': 'API для управления сотрудниками',
    'uiversion': 3,
    'openapi': '3.0.3',
    'specs': [
        {
            'endpoint': 'apispec_1',
            'route': '/apidocs/swagger.json',
            'rule_filter': lambda rule: True,
            'model_filter': lambda tag: True,
        }
    ],
    'specs_route': '/apidocs/',
    'description': 'API для управления сотрудниками компании',
    'termsOfService': '',
    'contact': {'email': 'admin@company.com'},
    'license': {'name': 'MIT'}
}
swagger = Swagger(app)

# Модель сотрудника для SQLite
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    
    def to_dict(self):
        """Возвращает данные сотрудника с гарантированным порядком полей"""
        return OrderedDict([
            ('id', self.id),
            ('name', self.name),
            ('surname', self.surname),
            ('position', self.position)
        ])

# Создание базы данных
with app.app_context():
    # Убедимся, что папка instance существует
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)
    db.create_all()

# Главная страница
@app.route('/')
def index():
    return send_file('index.html')

# Админ-панель
@app.route('/admin')
def admin():
    return send_file('admin.html')

# Страница Swagger
@app.route('/swagger')
def swagger_ui():
    return send_file('swagger.html')

# Serve favicon files
@app.route('/favicon/<path:filename>')
def favicon(filename):
    return send_from_directory('favicon', filename)

@app.route('/favicon.ico')
def favicon_ico():
    return send_from_directory('favicon', 'favicon.ico')

# API: Получить всех сотрудников
@app.route('/api/employees', methods=['GET'])
def get_employees():
    """
    Получить список всех сотрудников
    ---
    tags:
      - Сотрудники
    responses:
      200:
        description: Список всех сотрудников
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  name:
                    type: string
                    example: Иван
                  surname:
                    type: string
                    example: Иванов
                  position:
                    type: string
                    example: Разработчик
      500:
        description: Ошибка сервера
    """
    employees = Employee.query.all()
    return jsonify([emp.to_dict() for emp in employees])

# API: Получить сотрудника по ID
@app.route('/api/employees/<int:id>', methods=['GET'])
def get_employee_by_id(id):
    """
    Получить сотрудника по ID
    ---
    tags:
      - Сотрудники
    parameters:
      - in: path
        name: id
        schema:
          type: integer
        required: true
        description: ID сотрудника
        example: 1
    responses:
      200:
        description: Данные сотрудника
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                name:
                  type: string
                  example: Иван
                surname:
                  type: string
                  example: Иванов
                position:
                  type: string
                  example: Разработчик
      404:
        description: Сотрудник не найден
    """
    employee = Employee.query.get(id)
    if not employee:
        return jsonify({'error': 'Сотрудник не найден'}), 404
    return jsonify(employee.to_dict())

# API: Добавить сотрудника
@app.route('/api/employees', methods=['POST'])
def add_employee():
    """
    Добавить нового сотрудника
    ---
    tags:
      - Сотрудники
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - name
              - surname
              - position
            properties:
              name:
                type: string
                example: Иван
              surname:
                type: string
                example: Иванов
              position:
                type: string
                example: Разработчик
    responses:
      201:
        description: Сотрудник успешно добавлен
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                name:
                  type: string
                  example: Иван
                surname:
                  type: string
                  example: Иванов
                position:
                  type: string
                  example: Разработчик
      400:
        description: Неверные данные
    """
    data = request.get_json()
    if not data or not data.get('name') or not data.get('surname') or not data.get('position'):
        return jsonify({'error': 'Отсутствуют обязательные поля'}), 400
    
    # Создаем сотрудника через kwargs чтобы избежать ошибок анализатора
    new_employee = Employee(**{
        'name': data['name'],
        'surname': data['surname'],
        'position': data['position']
    })
    db.session.add(new_employee)
    db.session.commit()
    return jsonify(new_employee.to_dict()), 201

# API: Обновить сотрудника (PUT)
@app.route('/api/employees/<int:id>', methods=['PUT'])
def update_employee(id):
    """
    Полное обновление данных сотрудника
    ---
    tags:
      - Сотрудники
    parameters:
      - in: path
        name: id
        schema:
          type: integer
        required: true
        description: ID сотрудника
        example: 1
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - name
              - surname
              - position
            properties:
              name:
                type: string
                example: Иван
              surname:
                type: string
                example: Иванов
              position:
                type: string
                example: Старший разработчик
    responses:
      200:
        description: Сотрудник успешно обновлен
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                name:
                  type: string
                  example: Иван
                surname:
                  type: string
                  example: Иванов
                position:
                  type: string
                  example: Старший разработчик
      400:
        description: Неверные данные
      404:
        description: Сотрудник не найден
    """
    employee = Employee.query.get(id)
    if not employee:
        return jsonify({'error': 'Сотрудник не найден'}), 404
    
    data = request.get_json()
    if not data or not data.get('name') or not data.get('surname') or not data.get('position'):
        return jsonify({'error': 'Отсутствуют обязательные поля'}), 400
    
    employee.name = data['name']
    employee.surname = data['surname']
    employee.position = data['position']
    db.session.commit()
    return jsonify(employee.to_dict())

# API: Частичное обновление сотрудника (PATCH)
@app.route('/api/employees/<int:id>', methods=['PATCH'])
def patch_employee(id):
    """
    Частичное обновление данных сотрудника
    ---
    tags:
      - Сотрудники
    parameters:
      - in: path
        name: id
        schema:
          type: integer
        required: true
        description: ID сотрудника
        example: 1
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              name:
                type: string
                example: Иван
              surname:
                type: string
                example: Иванов
              position:
                type: string
                example: Team Lead
    responses:
      200:
        description: Сотрудник успешно обновлен
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                name:
                  type: string
                  example: Иван
                surname:
                  type: string
                  example: Иванов
                position:
                  type: string
                  example: Team Lead
      400:
        description: Неверные данные
      404:
        description: Сотрудник не найден
    """
    employee = Employee.query.get(id)
    if not employee:
        return jsonify({'error': 'Сотрудник не найден'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Отсутствуют данные для обновления'}), 400
    
    if 'name' in data:
        employee.name = data['name']
    if 'surname' in data:
        employee.surname = data['surname']
    if 'position' in data:
        employee.position = data['position']
    db.session.commit()
    return jsonify(employee.to_dict())

# API: Удалить сотрудника
@app.route('/api/employees/<int:id>', methods=['DELETE'])
def delete_employee(id):
    """
    Удалить сотрудника по ID
    ---
    tags:
      - Сотрудники
    parameters:
      - in: path
        name: id
        schema:
          type: integer
        required: true
        description: ID сотрудника
        example: 1
    responses:
      200:
        description: Сотрудник успешно удален
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Сотрудник успешно удален
      404:
        description: Сотрудник не найден
    """
    employee = Employee.query.get(id)
    if not employee:
        return jsonify({'error': 'Сотрудник не найден'}), 404
    
    db.session.delete(employee)
    db.session.commit()
    return jsonify({'message': 'Сотрудник успешно удален'})

# API: Удалить всех сотрудников
@app.route('/api/employees', methods=['DELETE'])
def delete_all_employees():
    """
    Удалить всех сотрудников
    ---
    tags:
      - Сотрудники
    responses:
      200:
        description: Все сотрудники успешно удалены или база уже пуста
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Все сотрудники успешно удалены
    """
    employees = Employee.query.all()
    if employees:
        for employee in employees:
            db.session.delete(employee)
        db.session.commit()
        return jsonify({'message': 'Все сотрудники успешно удалены'})
    else:
        return jsonify({'message': 'База сотрудников уже пуста'})

if __name__ == '__main__':
    app.run(debug=True)