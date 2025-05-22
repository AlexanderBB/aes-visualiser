// Embedded icons
const COPY_ICON_SRC = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' shape-rendering='geometricPrecision' text-rendering='geometricPrecision' image-rendering='optimizeQuality' fill-rule='evenodd' clip-rule='evenodd' viewBox='0 0 443 511.529'%3E%3Cpath fill='%233C4D7A' fill-rule='nonzero' d='M52.307 56.129h3.835v-3.822C56.142 23.598 79.74 0 108.449 0h282.244C419.416 0 443 23.585 443 52.307V403.08c0 28.548-23.759 52.307-52.307 52.307h-3.826v3.835c0 28.548-23.759 52.307-52.307 52.307H52.307C23.695 511.529 0 487.829 0 459.222V108.441c0-28.71 23.598-52.312 52.307-52.312z'/%3E%3Cpath fill='%23fff' d='M52.307 78.577h3.835V403.08c0 28.607 23.695 52.307 52.307 52.307h255.97v3.835c0 16.268-13.591 29.859-29.859 29.859H52.307c-16.268 0-29.859-13.43-29.859-29.859V108.441c0-16.43 13.431-29.864 29.859-29.864z'/%3E%3Cpath fill='%23fff' d='M108.448 22.446h282.244c16.428 0 29.86 13.592 29.86 29.861V403.08c0 16.268-13.592 29.86-29.86 29.86H108.448c-16.268 0-29.86-13.433-29.86-29.86V52.307c0-16.428 13.433-29.861 29.86-29.861z'/%3E%3C/svg%3E";

const CHECK_ICON_SRC = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath fill='%23007bff' d='M8 0a8 8 0 1 0 8 8A8.009 8.009 0 0 0 8 0Zm3.707 6.707-4 4a1 1 0 0 1-1.414 0l-2-2a1 1 0 0 1 1.414-1.414L7 8.586l3.293-3.293a1 1 0 0 1 1.414 1.414Z'/%3E%3C/svg%3E";

const MOON_ICON = "&#9790;"; // Moon symbol for night mode
const SUN_ICON = "&#9728;"; // Sun symbol for light mode

// Theme toggle functionality
function toggleTheme() {
    const body = document.body;
    const themeToggleBtn = document.getElementById('themeToggleBtn');

    // Toggle night mode class
    body.classList.toggle('night-mode');

    // Save preference to localStorage
    const isNightMode = body.classList.contains('night-mode');
    localStorage.setItem('nightMode', isNightMode);

    // Update button icon
    themeToggleBtn.innerHTML = isNightMode ? SUN_ICON : MOON_ICON;
}

// Check for saved theme preference
function loadThemePreference() {
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    if (!themeToggleBtn) return;

    const isNightMode = localStorage.getItem('nightMode') === 'true';

    if (isNightMode) {
        document.body.classList.add('night-mode');
        themeToggleBtn.innerHTML = SUN_ICON;
    } else {
        themeToggleBtn.innerHTML = MOON_ICON;
    }
}

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

        const isExpanded = target.classList.contains('visible');

        if (isExpanded) {
            // Hide the content
            target.classList.remove('visible');
            // Use setTimeout to set display:none after the animation completes
            setTimeout(() => {
                target.style.display = 'none';
            }, 300);
        } else {
            // Show the content
            target.style.display = 'block';
            // Use setTimeout to allow the browser to process the display change before adding the class
            setTimeout(() => {
                target.classList.add('visible');
            }, 10);
        }

        // Update the toggle button icon and text
        const toggleIcon = button.querySelector('.toggle-icon');
        const toggleText = button.querySelector('.toggle-text');

        if (isExpanded) {
            // Collapsing
            toggleIcon.textContent = '+';
            toggleText.textContent = 'View Detailed Explanation';
            toggleIcon.style.transform = 'rotate(0deg)';
        } else {
            // Expanding
            toggleIcon.textContent = '−'; // Using minus sign
            toggleText.textContent = 'Hide Detailed Explanation';
            toggleIcon.style.transform = 'rotate(90deg)';
        }

        button.classList.add('animate-click');
        setTimeout(() => button.classList.remove('animate-click'), 300);
    });
});

function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

const scrollTopBtn = document.getElementById('scrollTopBtn');

function toggleScrollButton() {
    if (!scrollTopBtn) return;

    if (window.scrollY > 100) {
        scrollTopBtn.style.display = 'flex';
    } else {
        scrollTopBtn.style.display = 'none';
    }
}

window.addEventListener('scroll', toggleScrollButton);

// Run it once on page load too
window.addEventListener('load', toggleScrollButton);

if (scrollTopBtn) {
    scrollTopBtn.addEventListener('click', scrollToTop);
}

// Character counter functionality
function setupCharacterCounters() {
    const keyInput = document.getElementById('key');
    const wordInput = document.getElementById('word');
    const keyCounter = document.getElementById('keyCounter');
    const wordCounter = document.getElementById('wordCounter');

    if (keyInput && keyCounter) {
        // Update initial count
        keyCounter.textContent = keyInput.value.length;

        // Add event listener for input changes
        keyInput.addEventListener('input', function() {
            keyCounter.textContent = this.value.length;

            // Add visual feedback
            if (this.value.length === 16) {
                keyCounter.classList.add('complete');
            } else {
                keyCounter.classList.remove('complete');
            }
        });
    }

    if (wordInput && wordCounter) {
        // Update initial count
        wordCounter.textContent = wordInput.value.length;

        // Add event listener for input changes
        wordInput.addEventListener('input', function() {
            wordCounter.textContent = this.value.length;

            // Add visual feedback
            if (this.value.length === 16) {
                wordCounter.classList.add('complete');
            } else {
                wordCounter.classList.remove('complete');
            }
        });
    }
}

// Handle toggle for Rounds 2-9
function setupRounds2to9Toggle() {
    const toggleBtn = document.getElementById('toggleRounds2to9Btn');
    if (!toggleBtn) return;

    const rounds2to9Steps = document.querySelectorAll('.rounds2to9-step');

    toggleBtn.addEventListener('click', function() {
        const isExpanded = toggleBtn.getAttribute('data-expanded') === 'true';

        if (isExpanded) {
            // Hide rounds 2-9
            rounds2to9Steps.forEach(step => {
                step.style.display = 'none';
            });

            // Update button
            toggleBtn.querySelector('.toggle-icon').textContent = '+';
            toggleBtn.querySelector('.toggle-text').textContent = 'Show Rounds 2-9';
            toggleBtn.setAttribute('data-expanded', 'false');
        } else {
            // Show rounds 2-9
            rounds2to9Steps.forEach(step => {
                step.style.display = 'flex';
                // Trigger animation
                setTimeout(() => {
                    step.style.animation = 'fadeInStep 1s forwards';
                }, 10);
            });

            // Update button
            toggleBtn.querySelector('.toggle-icon').textContent = '−';
            toggleBtn.querySelector('.toggle-text').textContent = 'Hide Rounds 2-9';
            toggleBtn.setAttribute('data-expanded', 'true');
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    // Load theme preference
    loadThemePreference();

    // Add event listener to theme toggle button
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', toggleTheme);
    }

    // Setup character counters for input fields
    setupCharacterCounters();

    // Setup toggle for Rounds 2-9
    setupRounds2to9Toggle();

    // Animate steps if they exist (except rounds 2-9 which are hidden initially)
    const steps = document.querySelectorAll('.step:not(.rounds2to9-step)');
    if (steps.length > 0) {
        steps.forEach((step, index) => {
            setTimeout(() => {
                step.style.animation = 'fadeInStep 1s forwards';
            }, index * 800);
        });
    }
});
