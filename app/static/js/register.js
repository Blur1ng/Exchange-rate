document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('register-form');
    const errorMessage = document.getElementById('error-message');  // Если есть элемент для ошибок

    form.addEventListener('submit', async function(event) {
        event.preventDefault();  // Предотвращаем перезагрузку страницы

        const username = document.querySelector('input[name="username"]').value;
        const password = document.querySelector('input[name="password"]').value;
        const confirmPassword = document.querySelector('input[name="confirm_password"]').value;

        // Проверяем совпадение паролей
        if (password !== confirmPassword) {
            if (errorMessage) {
                errorMessage.textContent = 'Пароли не совпадают!';
            }
            return;  // Останавливаем выполнение, если пароли не совпадают
        }

        const registerData = {
            username: username,
            password: password
        };

        try {
            const response = await fetch('/api/v1/auth/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(registerData),
            });

            if (response.ok) {
                const data = await response.json();
                window.location.href = '/login';  // Перенаправление на страницу входа
            } else {
                const errorData = await response.json();
                if (errorMessage) {
                    errorMessage.textContent = errorData.detail;
                }
            }
        } catch (error) {
            if (errorMessage) {
                errorMessage.textContent = 'Произошла ошибка. Попробуйте позже.';
            }
        }
    });
});
