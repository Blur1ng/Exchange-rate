document.addEventListener("DOMContentLoaded", () => {
    let ws
    let currentMultiplier = 0
    let gameActive = false
  
    const resultContainer = document.getElementById("result")
    const multiplierContainer = document.getElementById("multiplierContainer")
    const multiplierValue = document.getElementById("multiplierValue")
    const takeProfitBtn = document.getElementById("takeProfitBtn")
    const submitBtn = document.getElementById("submitBtn")
    const betInput = document.getElementById("start_bet")
    const rocketAnimation = document.getElementById("rocketAnimation")
    const rocket = document.getElementById("rocket")
  
    // Reset game
    function resetGame() {
      gameActive = false
      currentMultiplier = 0
      multiplierValue.textContent = "0.0x"
      multiplierValue.classList.remove("pulse")
      takeProfitBtn.classList.remove("show")
      multiplierContainer.classList.remove("show")
      resultContainer.classList.remove("show")
      rocketAnimation.classList.remove("active")
      rocket.classList.remove("fly-away")
      submitBtn.disabled = false
      betInput.disabled = false
    }
  
    // Start game
    submitBtn.addEventListener("click", async (e) => {
      e.preventDefault()
  
      const betAmount = betInput.value
      if (!betAmount || betAmount < 10) {
        alert("Минимальная ставка: 10")
        return
      }
  
      resetGame()
      gameActive = true
  
      submitBtn.disabled = true
      betInput.disabled = true
  
      multiplierContainer.classList.add("show")
      rocketAnimation.classList.add("active")
  
      ws = new WebSocket(`ws://${window.location.host}/api/v1/ws/rocket/`)
  
      const message = {
        action: "start_bet",
        betValue: betAmount,
      }
  
      ws.onopen = () => {
        ws.send(JSON.stringify(message))
        takeProfitBtn.classList.add("show")
        multiplierValue.classList.add("pulse")
      }
  
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
  
        if (data.action === "update_multiplier") {
          currentMultiplier = data.value
          multiplierValue.textContent = `${currentMultiplier.toFixed(1)}x`
  
          // добавления анимации ракете обновл позиции
          const rocketPosition = Math.min(currentMultiplier * 10, 100)
          rocket.style.bottom = `${rocketPosition}%`
        } else if (data.status) {
          gameActive = false
          multiplierValue.classList.remove("pulse")
  
          if (data.status === "WIN") {
            resultContainer.innerHTML = `<span class="result-win">ПОБЕДА! +${data.end_bet}₽</span>`

          } else {
            resultContainer.innerHTML = `<span class="result-lose">ПРОИГРЫШ -${data.end_bet}₽</span>`

            rocket.classList.add("fly-away")
          }
  
          resultContainer.classList.add("show")
          takeProfitBtn.classList.remove("show")
  
          setTimeout(() => {
            submitBtn.disabled = false
            betInput.disabled = false
          }, 1500)
        }
      }
  
      ws.onerror = (error) => {
        console.error("WebSocket error:", error)
        resetGame()
        resultContainer.innerHTML = `<span class="result-lose">Ошибка соединения</span>`
        resultContainer.classList.add("show")
      }
  
      ws.onclose = () => {
        if (gameActive) {
          resetGame()
          resultContainer.innerHTML = `<span class="result-lose">Соединение прервано</span>`
          resultContainer.classList.add("show")
        }
      }
    })
  
    takeProfitBtn.addEventListener("click", (e) => {
      e.preventDefault()
  
      if (!gameActive) return
  
      const message = {
        action: "take_profit",
      }
  
      ws.send(JSON.stringify(message))
      takeProfitBtn.classList.remove("show")
    })
  })
  
  