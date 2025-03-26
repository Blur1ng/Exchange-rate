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
        try {
            // Формируем данные для отправки
            const formData = {
                exchange: document.getElementById("currency").value,
                bet_amount: parseFloat(document.getElementById("amount").value),
                leverage: parseInt(document.getElementById("leverage").value),
                direction: document.getElementById("direction").value,
                time: parseInt(document.getElementById("time").value),
            };
            // 2 Отправляем данные для сохранения ставки
            const tradeResponse = await fetch("/api/v1/trade_it/", {
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
            price_show.innerText = `${formData.exchange}:  ${result.start_price.toFixed(4)}$`;
            container_show1.classList.add("show");
            

            // Функция для проверки статуса
            function connectWebSocket(tradeId) {
                const ws = new WebSocket(`ws://${window.location.host}/api/v1/ws/trade_status/${tradeId}`);
            
                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    
                    if (data.error) {
                        console.error('WebSocket error:', data.error);
                        return;
                    }
            
                    if (data.status === "completed") {
                        current_show.innerText = `${formData.exchange}:  ${data.end_price.toFixed(4)}$`;
                        container_show2.classList.add("show");
                        resultContainer.innerText = data.result === "W" 
                            ? `Победа! +${formData.bet_amount * formData.leverage}₽`
                            : `Проигрыш -${formData.bet_amount * formData.leverage}₽`;
                    } 
                    else if (data.status === "failed") {
                        resultContainer.innerText = `Trade: ${tradeId} was failed`;
                    }
                };
            }         
            connectWebSocket(result.trade_id);
            
        } catch (error) {
            resultContainer.innerText = "Ошибка: " + error.message;
            resultContainer.classList.add("show");
            console.error(error)
        }
    });
});
