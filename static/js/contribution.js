function renderTaskContribution(taskId, activityDates) {
    const container = document.getElementById('task-' + taskId);
    if (!container) {
        console.error("Container not found for task ID:", taskId);
        return;
    }

    // Очистить контейнер перед перерисовкой
    container.innerHTML = '';

    const today = new Date();
    const totalDays = 30; // максимум 30 дней

    // === Добавляем контроль ширины окна ===
    let daysToShow;
    const screenWidth = window.innerWidth;

    if (screenWidth > 1200) {
        daysToShow = 30;
    } else if (screenWidth > 992) {
        daysToShow = 24;
    } else if (screenWidth > 768) {
        daysToShow = 18;
    } else if (screenWidth > 576) {
        daysToShow = 12;
    } else {
        daysToShow = 8;
    }
    // === Конец контроля ширины ===

    const startDate = new Date();
    startDate.setDate(today.getDate() - daysToShow + 1);

    for (let d = new Date(startDate); d <= today; d.setDate(d.getDate() + 1)) {
        const dateStr = d.toISOString().slice(0, 10);
        const square = document.createElement('div');
        square.classList.add('square');
        if (activityDates.includes(dateStr)) {
            square.classList.add('filled');
        }
        container.appendChild(square);
    }
}