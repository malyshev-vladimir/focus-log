from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
from datetime import datetime, date

app = Flask(__name__)
TASKS_FILE = 'tasks.json'


@app.template_filter('datetimeformat')
def format_datetime(value):
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime('%d.%m.%Y')
    except Exception:
        return value


def load_data():
    if not os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"tasks": [], "logs_by_date": {}}, f)
    with open(TASKS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_data(data):
    temp_file = TASKS_FILE + '.tmp'
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(temp_file, TASKS_FILE)


@app.route('/', methods=['GET'])
def daily_log():
    data = load_data()
    today = date.today()
    today_str = today.isoformat()
    current_date = today.strftime('%d.%m.%Y')

    tasks = sorted(
        [t for t in data.get("tasks", []) if not t.get("completed", False)],
        key=lambda t: t.get("priority", 10)
    )

    logs_by_date = data.get("logs_by_date", {})
    today_log = logs_by_date.get(today_str, {})

    general_notes = today_log.get("general_notes", "")
    task_entries = today_log.get("entries", {})

    return render_template(
        "daily.html",
        tasks=tasks,
        general_notes=general_notes,
        task_entries=task_entries,
        current_date=current_date,
        logs_by_date=logs_by_date
    )


@app.route('/save_log', methods=['POST'])
def save_log():
    data = load_data()
    form_data = request.form.to_dict()
    today = date.today().isoformat()

    tasks = data.get("tasks", [])
    logs_by_date = data.get("logs_by_date", {})

    daily_entry = {
        "general_notes": form_data.get("general_notes", "").strip(),
        "entries": {}
    }

    for task in tasks:
        field_name = f"entry_{task['created_at']}"
        if field_name in form_data:
            text = form_data[field_name].strip()
            if text:
                daily_entry["entries"][task["created_at"]] = text

    logs_by_date[today] = daily_entry
    data["logs_by_date"] = logs_by_date
    save_data(data)

    return redirect(url_for('daily_log'))


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    data = load_data()
    tasks = data.get("tasks", [])

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

        data["tasks"] = tasks
        save_data(data)
        return redirect(url_for('settings'))

    tasks = sorted(tasks, key=lambda t: t.get("priority", 10))
    return render_template('settings.html', tasks=tasks)


@app.route('/delete_task', methods=['POST'])
def delete_task():
    created_at = request.form.get('created_at')
    data = load_data()
    tasks = data.get("tasks", [])
    tasks = [t for t in tasks if t['created_at'] != created_at]
    data["tasks"] = tasks
    save_data(data)
    return redirect(url_for('settings'))


@app.route('/edit_task', methods=['POST'])
def edit_task():
    edit_data = request.get_json()
    data = load_data()
    tasks = data.get("tasks", [])
    created_at = edit_data.get('created_at')

    for task in tasks:
        if task['created_at'] == created_at:
            task['name'] = edit_data.get('name', task['name']).strip()
            try:
                task['priority'] = int(edit_data.get('priority', task['priority']))
            except (ValueError, TypeError):
                pass
            data["tasks"] = tasks
            save_data(data)
            return jsonify({'status': 'ok'})

    return jsonify({'status': 'error'})


@app.route('/toggle_task', methods=['POST'])
def toggle_task():
    created_at = request.form.get('created_at')
    data = load_data()
    tasks = data.get("tasks", [])
    for task in tasks:
        if task['created_at'] == created_at:
            task['completed'] = not task.get('completed', False)
            break
    data["tasks"] = tasks
    save_data(data)
    return redirect(url_for('settings'))


if __name__ == '__main__':
    app.run(debug=True)
