/**
 * Fluir - Landing Page
 * Smooth scroll + Countdown timer NR-1
 */

/* ── Smooth scroll para âncoras ── */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            target.scrollIntoView({ behavior: prefersReducedMotion ? 'auto' : 'smooth' });
        }
    });
});

/* ── Countdown timer → 26/05/2026 00:00 BRT ── */
(function initCountdown() {
    const deadline = new Date('2026-05-26T00:00:00-03:00').getTime();
    const $days = document.getElementById('countDays');
    const $hours = document.getElementById('countHours');
    const $min = document.getElementById('countMin');

    if (!$days || !$hours || !$min) return;

    function tick() {
        const now = Date.now();
        const diff = deadline - now;

        if (diff <= 0) {
            $days.textContent = '0';
            $hours.textContent = '0';
            $min.textContent = '0';
            return;
        }

        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

        $days.textContent = days;
        $hours.textContent = String(hours).padStart(2, '0');
        $min.textContent = String(mins).padStart(2, '0');
    }

    tick();
    setInterval(tick, 30000); // atualiza a cada 30s (não precisa de 1s pois mostra minutos)
})();
