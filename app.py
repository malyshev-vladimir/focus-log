from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
TASKS_FILE = 'tasks.json'


def load_tasks():
    if not os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
    with open(TASKS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_tasks(tasks):
    temp_file = TASKS_FILE + '.tmp'
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    os.replace(temp_file, TASKS_FILE)


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
            return redirect(url_for('settings'))

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

        save_tasks(tasks)
        return redirect(url_for('settings'))

    return render_template('settings.html', tasks=tasks)


@app.route('/delete_task', methods=['POST'])
def delete_task():
    created_at = request.form.get('created_at')
    tasks = load_tasks()
    tasks = [t for t in tasks if t['created_at'] != created_at]
    save_tasks(tasks)
    return redirect(url_for('settings'))


@app.route('/edit_task', methods=['POST'])
def edit_task():
    data = request.get_json()
    tasks = load_tasks()
    created_at = data.get('created_at')
    for task in tasks:
        if task['created_at'] == created_at:
            task['name'] = data.get('name', task['name']).strip()
            try:
                task['priority'] = int(data.get('priority', task['priority']))
            except (ValueError, TypeError):
                pass
            save_tasks(tasks)
            return jsonify({'status': 'ok'})
    return jsonify({'status': 'error'})


@app.route('/toggle_task', methods=['POST'])
def toggle_task():
    created_at = request.form.get('created_at')
    tasks = load_tasks()
    for task in tasks:
        if task['created_at'] == created_at:
            task['completed'] = not task.get('completed', False)
            break
    save_tasks(tasks)
    return redirect(url_for('settings'))


if __name__ == '__main__':
    app.run(debug=True)
