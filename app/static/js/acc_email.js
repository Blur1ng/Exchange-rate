document.getElementById("email-form").addEventListener("submit", async function(event) {
    event.preventDefault();  // Отменяем стандартное поведение формы (переход по URL)

    const newEmail = document.getElementById("new_email").value;
    
    const response = await fetch(`/api/v1/update_account/${newEmail}`);
});