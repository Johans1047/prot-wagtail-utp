(function () {
    const slides = document.querySelectorAll('.winners-slide');
    const dots   = document.querySelectorAll('.winners-dot');
    const prev   = document.getElementById('winners-prev');
    const next   = document.getElementById('winners-next');
    let current  = 0;
    let timer;

    if (!slides.length || !dots.length) {
        return;
    }

    function render(index) {
        slides.forEach(function (slide, i) {
            if (i === index) {
                slide.classList.remove('hidden');
            } else {
                slide.classList.add('hidden');
            }
        });

        dots.forEach(function (dot, i) {
            if (i === index) {
                dot.classList.add('bg-cobalt-800', 'text-primary-foreground');
                dot.classList.remove('bg-primary-foreground/10', 'text-primary-foreground/70');
            } else {
                dot.classList.remove('bg-cobalt-800', 'text-primary-foreground');
                dot.classList.add('bg-primary-foreground/10', 'text-primary-foreground/70');
            }
        });
    }

    function goTo(index) {
        current = (index + slides.length) % slides.length;
        render(current);
    }

    function startTimer() {
        timer = setInterval(function () { goTo(current + 1); }, 6000);
    }

    function resetTimer() {
        clearInterval(timer);
        startTimer();
    }

    if (prev) {
        prev.addEventListener('click', function () {
            goTo(current - 1);
            resetTimer();
        });
    }

    if (next) {
        next.addEventListener('click', function () {
            goTo(current + 1);
            resetTimer();
        });
    }

    dots.forEach(function (dot) {
        dot.addEventListener('click', function () {
            goTo(parseInt(this.dataset.index));
            resetTimer();
        });
    });

    render(0);
    startTimer();
}());