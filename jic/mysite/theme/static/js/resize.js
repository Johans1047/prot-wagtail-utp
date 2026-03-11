function initLogoResize() {
    const headerLogo = document.getElementById("header-logo");
    const jicLogo = document.getElementById("jic-logo");

    function updateLogoSizes() {
        const width = window.innerWidth;

        if (headerLogo) {
            if (width >= 1024) {
                headerLogo.style.height = "2.25rem";
            } else if (width >= 768) {
                headerLogo.style.height = "2rem";
            } else {
                headerLogo.style.height = "1.5rem";
            }
        }

        if (jicLogo) {
            if (width >= 1024) {
                jicLogo.style.height = "15rem";
            } else if (width >= 768) {
                jicLogo.style.height = "12rem";
            } else {
                jicLogo.style.height = "9rem";
            }
        }
    }

    updateLogoSizes();
    window.addEventListener("resize", updateLogoSizes);
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initLogoResize);
} else {
    initLogoResize();
}
