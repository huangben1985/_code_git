# Description: A simple To-Do list application using Flask and SQLAlchemy
# Instructoin via: https://www.youtube.com/watch?v=Z1RJmh_OqeA
# github:   https://github.com/jakerieger/FlaskIntroduction

from flask import Flask, render_template,url_for,request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize the Flask application
app = Flask(__name__)   

# Configure the SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Initialize the SQLAlchemy object
db = SQLAlchemy(app)

# Define the Todo model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    content = db.Column(db.String(200), nullable=False)  # Task content
    completed = db.Column(db.Boolean)  # Task completion status
    date_created = db.Column(db.DateTime, default=datetime.utcnow)  # Task creation date
    date_completed = db.Column(db.DateTime, default=None)  # Task completion date

    def __repr__(self):
        return '<Task %r>' % self.id

# Define the index route to handle adding and displaying tasks
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content, completed=False)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)

# Define the delete route to handle deleting tasks
@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

# Define the update route to handle updating tasks
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form.get('content')
        task.completed = request.form.get("completed") == "true"
        task.date_completed = datetime.utcnow() if task.completed else None

        try:
            db.session.commit()
            return redirect('/')
        except Exception as e:
            print(f"Error updating task: {e}")
            return 'There was an issue updating your task'

    return render_template('update.html', task=task)


# Run the application
if __name__ == '__main__':
    app.run(debug=True)