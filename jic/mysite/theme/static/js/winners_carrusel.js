(function () {
    const slides = document.querySelectorAll('.winners-slide');
    const dots   = document.querySelectorAll('.winners-dot');
    let current  = 0;
    let timer;

    function goTo(index) {
        slides[current].classList.add('hidden');
        dots[current].classList.remove('bg-amber-400', 'text-amber-950');
        dots[current].classList.add('bg-primary-foreground/10', 'text-primary-foreground/70');

        current = (index + slides.length) % slides.length;

        slides[current].classList.remove('hidden');
        dots[current].classList.add('bg-amber-400', 'text-amber-950');
        dots[current].classList.remove('bg-primary-foreground/10', 'text-primary-foreground/70');
    }

    function startTimer() {
        timer = setInterval(function () { goTo(current + 1); }, 6000);
    }

    function resetTimer() {
        clearInterval(timer);
        startTimer();
    }

    document.getElementById('winners-prev').addEventListener('click', function () {
        goTo(current - 1);
        resetTimer();
    });

    document.getElementById('winners-next').addEventListener('click', function () {
        goTo(current + 1);
        resetTimer();
    });

    dots.forEach(function (dot) {
        dot.addEventListener('click', function () {
            goTo(parseInt(this.dataset.index));
            resetTimer();
        });
    });

    startTimer();
}());