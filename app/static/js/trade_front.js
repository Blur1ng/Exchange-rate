document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("tradeForm");
    const resultContainer = document.getElementById("result");

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        // Получаем текущий курс выбранного актива
        let start_price;
        let user_name;
        const exchange = document.getElementById("currency").value;

        try {
            // Запрос курса для выбранного обмена
            let response;
            response = await fetch(`/api/v1/rate/coin/${exchange}/`);
            const data_coin = await response.json();
            start_price = data_coin[`${exchange}USDT`];

            // 1 Получаем имя пользователя из JWT токена
            response = await fetch(`/api/v1/verify_jwt_token/`);
            const data = await response.json();
            user_name = data.user_name;

            // Формируем данные для отправки
            const formData = {
                exchange: exchange,
                bet_amount: parseFloat(document.getElementById("amount").value),
                leverage: parseInt(document.getElementById("leverage").value),
                direction: document.getElementById("direction").value,
                time: parseInt(document.getElementById("time").value),
                start_price: start_price,
                user_name: user_name,
            };

            // 2 Отправляем данные для сохранения ставки
            const tradeResponse = await fetch("/api/v1/trade_it", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "include",
                body: JSON.stringify(formData),
            });

            const result = await tradeResponse.json();
        
            resultContainer.innerText = `Сделка создана! ID: ${result.trade_id}`;
            resultContainer.classList.add("show");

            // Функция для проверки статуса
            const checkStatus = async () => {
                const response = await fetch(`/api/v1/trade_status/${result.trade_id}`);
                const data = await response.json();
                
                if (data.status === "completed") {
                    resultContainer.innerText = data.result === "W" 
                        ? `Победа! +${formData.bet_amount * formData.leverage}$`
                        : `Проигрыш -${formData.bet_amount * formData.leverage}$`;
                } else if (data.status === "pending") {
                    setTimeout(checkStatus, 5000); // Проверяем каждые 5 секунд
                }
            };
            resultContainer.classList.add("show");
            checkStatus();

        } catch (error) {
            resultContainer.innerText = "Ошибка: " + error.message;
            resultContainer.classList.add("show");
        }
    });
});
