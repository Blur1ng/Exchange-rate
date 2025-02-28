document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("tradeForm");
    const resultContainer = document.getElementById("result");
    const container_peredv = document.getElementById("container-peredv");
    const container_show1 = document.getElementById("container1-show");
    const price_show = document.getElementById("price-show");
    const container_show2 = document.getElementById("container2-show");
    const current_show = document.getElementById("current-show");

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
            
            //смещение контейнера
            container_peredv.classList.add("show");  
            
            // контейнтейнеры цен
            price_show.innerText = `${exchange}:  ${start_price.toFixed(4)}$`;
            container_show1.classList.add("show");

            // Функция для проверки статуса
            function connectWebSocket(tradeId) {
                const ws = new WebSocket(`ws://${window.location.host}/api/v1/ws/trade_status/${tradeId}`);
            
                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    console.log("Received data:", event.data);
                    
                    if (data.error) {
                        console.error('WebSocket error:', data.error);
                        return;
                    }
            
                    if (data.status === "completed") {
                        current_show.innerText = `${exchange}:  ${data.end_price.toFixed(4)}$`;
                        container_show2.classList.add("show");
                        resultContainer.innerText = data.result === "W" 
                            ? `Победа! +${formData.bet_amount * formData.leverage}$`
                            : `Проигрыш -${formData.bet_amount * formData.leverage}$`;
                    } 
                    else if (data.status === "failed") {
                        resultContainer.innerText = `Trade: ${tradeId} was failed`;
                    }
                };
            
                ws.onclose = (event) => {
                    if (!event.wasClean) {
                        setTimeout(() => connectWebSocket(tradeId), 5000);
                    }
                };
            }         
            connectWebSocket(result.trade_id);
            
        } catch (error) {
            resultContainer.innerText = "Ошибка: " + error.message;
            resultContainer.classList.add("show");
        }
    });
});
