from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)
TASKS_FILE = 'tasks.json'

# Create JSON file if not exists
if not os.path.exists(TASKS_FILE):
    with open(TASKS_FILE, 'w') as f:
        json.dump([], f)


def load_tasks():
    with open(TASKS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


@app.route('/')
def home():
    return redirect(url_for('settings'))


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    tasks = load_tasks()

    if request.method == 'POST':
        new_task = request.form.get('task')
        priority_str = request.form.get('priority')

        if not new_task or not new_task.strip():
            return redirect(url_for('settings'))  # skip empty

        new_task = new_task.strip()

        try:
            priority = int(priority_str)
        except (ValueError, TypeError):
            priority = 10

        tasks.append({
            "name": new_task,
            "priority": priority,
            "created_at": datetime.now().isoformat(timespec='seconds'),
            "completed": False
        })

        # Safe write
        temp_file = TASKS_FILE + '.tmp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        os.replace(temp_file, TASKS_FILE)

        return redirect(url_for('settings'))

    return render_template('settings.html', tasks=tasks)



if __name__ == '__main__':
    app.run(debug=True)