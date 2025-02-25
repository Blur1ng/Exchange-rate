document.addEventListener("DOMContentLoaded", async function () {
    try {
        const response = await fetch("/api/v1/verify_jwt_token", {
            method: "GET",
            credentials: "include",
        });

        if (!response.ok) {
            // Если токен недействителен, перенаправляем на страницу входа
            window.location.href = "/login";
            return;
        }

        // Если токен действителен, загружаем страницу
    } catch (error) {
        console.error("Error verifying JWT token:", error);
        window.location.href = "/login";
    }
});