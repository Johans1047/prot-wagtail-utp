document.addEventListener("DOMContentLoaded", function () {
    const messages = document.querySelectorAll('[role="alert"]');
    messages.forEach((msg) => {
        setTimeout(() => {
            msg.style.animation = "fadeOut 0.4s ease-out forwards";
            setTimeout(() => msg.remove(), 400);
        }, 5000);
    });
});
