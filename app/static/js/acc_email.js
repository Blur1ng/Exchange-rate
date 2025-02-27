document.getElementById("email-form").addEventListener("submit", async function(event) {
    event.preventDefault();  // Отменяем стандартное поведение формы (переход по URL)

    const newEmail = document.getElementById("new_email").value;
    
    try {
        const response = await fetch(`/api/v1/update_account/${newEmail}/`, { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();

        if (response.ok) {
            showNotification(data.message || 'Email успешно обновлен!', 'success');
        } else {
            showNotification(data.message || 'Ошибка при обновлении email', 'error');
        }
    } catch (error) {
        showNotification('Ошибка при подключении к серверу', 'error');
    }
});

function showNotification(message, type) {
    const notification = document.getElementById('email-notification');
    const messageSpan = document.getElementById('email-message');
    messageSpan.textContent = message;

    if (type === 'success') {
        notification.style.backgroundColor = 'rgba(144, 238, 144, 0.8)';  // Зеленый
    } else {
        notification.style.backgroundColor = 'rgba(255, 99, 71, 0.8)';  // Красный
    }

    notification.classList.add('show');
    setTimeout(() => {
        notification.classList.remove('show');
    }, 5000);  // Скрыть уведомление через 5 секунд
}
