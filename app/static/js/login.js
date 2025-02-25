document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');  // Если есть элемент для ошибок
    form.addEventListener('submit', async function(event) {
        event.preventDefault();  // Предотвращаем перезагрузку страницы

        const username = document.querySelector('input[name="username"]').value;
        const password = document.querySelector('input[name="password"]').value;

        const loginData = {
            username: username,
            password: password
        };

        try {
            const response = await fetch('/api/v1/auth/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(loginData),
            });

            if (response.ok) {
                const data = await response.json();
                window.location.href = '/';
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
