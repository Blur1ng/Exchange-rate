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
            if (exchange === "BTC" || exchange === "ETH") {
                response = await fetch(`/api/v1/rate/coin/${exchange}/`);
                const data = await response.json();
                start_price = data[`${exchange}USDT`];
            } else {
                response = await fetch(`/api/v1/rate/rub_to/${exchange}/`);
                const data = await response.json();
                start_price = parseFloat(data[exchange].replace(",", "."));
            }

            // Получаем имя пользователя из JWT токена
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

            // Отправляем данные для сохранения ставки
            const tradeResponse = await fetch("/api/v1/trade_it", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "include",
                body: JSON.stringify(formData),
            });

            if (!tradeResponse.ok) {
                throw new Error("Ошибка при размещении ставки");
            }

            const result = await tradeResponse.json();
            resultContainer.innerText = `Сделка успешно состоялась!`;
            resultContainer.classList.add("show");

            // Ожидание указанного времени и затем отправка данных для расчета результата
            setTimeout(async () => {
                try {
                    response = await fetch(`/api/v1/rate/coin/${exchange}/`);
                    const data = await response.json();
                    const end_price = data[`${exchange}USDT`];

                    const endData = {
                        trade_id: result.trade_id,
                        end_price: end_price,
                    };

                    const EndTradeResponse = await fetch("/api/v1/check_trade/", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        credentials: "include",
                        body: JSON.stringify(endData),
                    });

                    const checkResult = await EndTradeResponse.json();
                    resultContainer.innerText = checkResult.message;
                    resultContainer.classList.add("show");
                } catch (error) {
                    resultContainer.innerText = "Ошибка при получении данных для расчета результата: " + error.message;
                    resultContainer.classList.add("show");
                }
            }, formData.time * 60 * 1000); // Ждем указанное время в минутах
        } catch (error) {
            resultContainer.innerText = "Ошибка: " + error.message;
            resultContainer.classList.add("show");
        }
    });
});
