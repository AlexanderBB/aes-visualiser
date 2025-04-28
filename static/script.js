// Embedded icons
const COPY_ICON_SRC = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' shape-rendering='geometricPrecision' text-rendering='geometricPrecision' image-rendering='optimizeQuality' fill-rule='evenodd' clip-rule='evenodd' viewBox='0 0 443 511.529'%3E%3Cpath fill='%233C4D7A' fill-rule='nonzero' d='M52.307 56.129h3.835v-3.822C56.142 23.598 79.74 0 108.449 0h282.244C419.416 0 443 23.585 443 52.307V403.08c0 28.548-23.759 52.307-52.307 52.307h-3.826v3.835c0 28.548-23.759 52.307-52.307 52.307H52.307C23.695 511.529 0 487.829 0 459.222V108.441c0-28.71 23.598-52.312 52.307-52.312z'/%3E%3Cpath fill='%23fff' d='M52.307 78.577h3.835V403.08c0 28.607 23.695 52.307 52.307 52.307h255.97v3.835c0 16.268-13.591 29.859-29.859 29.859H52.307c-16.268 0-29.859-13.43-29.859-29.859V108.441c0-16.43 13.431-29.864 29.859-29.864z'/%3E%3Cpath fill='%23fff' d='M108.448 22.446h282.244c16.428 0 29.86 13.592 29.86 29.861V403.08c0 16.268-13.592 29.86-29.86 29.86H108.448c-16.268 0-29.86-13.433-29.86-29.86V52.307c0-16.428 13.433-29.861 29.86-29.861z'/%3E%3C/svg%3E";

const CHECK_ICON_SRC = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath fill='%23007bff' d='M8 0a8 8 0 1 0 8 8A8.009 8.009 0 0 0 8 0Zm3.707 6.707-4 4a1 1 0 0 1-1.414 0l-2-2a1 1 0 0 1 1.414-1.414L7 8.586l3.293-3.293a1 1 0 0 1 1.414 1.414Z'/%3E%3C/svg%3E";
// -------- Actual working code below --------

// Handle copy buttons
const copyButtons = document.querySelectorAll('.copy-icon-btn');
copyButtons.forEach(button => {
    const img = button.querySelector('img');
    img.src = COPY_ICON_SRC; // embedded SVG icon

    button.addEventListener('click', function() {
        const targetId = button.dataset.target;
        const target = document.getElementById(targetId);
        if (!target) return;

        let text = '';
        const table = target.querySelector('table');
        if (table) {
            const rows = table.querySelectorAll('tr');
            rows.forEach((row, idx) => {
                if (idx === 0) return; // Skip header
                const cols = row.querySelectorAll('td');
                if (cols.length === 2) {
                    text += cols[0].innerText + " " + cols[1].innerText + "\n";
                }
            });
        }

        navigator.clipboard.writeText(text.trim()).then(() => {
            img.src = CHECK_ICON_SRC; // temporarily show success icon
            const copiedText = button.querySelector('.copied-text');
            copiedText.classList.add('show');

            setTimeout(() => {
                copiedText.classList.remove('show');
                img.src = COPY_ICON_SRC; // reset to copy icon
            }, 1500);
        });
    });
});

// Handle toggle (View Details) buttons
const toggleButtons = document.querySelectorAll('.toggle-btn');
toggleButtons.forEach(button => {
    button.addEventListener('click', function() {
        const targetId = button.dataset.target;
        const target = document.getElementById(targetId);
        if (!target) return;

        target.style.display = (target.style.display === 'none' ? 'block' : 'none');

        button.classList.add('animate-click');
        setTimeout(() => button.classList.remove('animate-click'), 300);
    });
});

function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

const scrollTopBtn = document.getElementById('scrollTopBtn');

function toggleScrollButton() {
    if (window.scrollY > 100) {
        scrollTopBtn.style.display = 'flex';
    } else {
        scrollTopBtn.style.display = 'none';
    }
}

window.addEventListener('scroll', toggleScrollButton);

// Run it once on page load too
window.addEventListener('load', toggleScrollButton);

scrollTopBtn.addEventListener('click', scrollToTop);

document.addEventListener('DOMContentLoaded', function () {
    const steps = document.querySelectorAll('.step');
    steps.forEach((step, index) => {
        setTimeout(() => {
            step.style.animation = 'fadeInStep 1s forwards';
        }, index * 800);
    });
});
