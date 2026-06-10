/**
 * Portfolio — expand/collapse interaction for project details.
 */
(function () {
    'use strict';

    const toggleButtons = document.querySelectorAll('.project__toggle');

    toggleButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            const targetId = button.getAttribute('aria-controls');
            const details = document.getElementById(targetId);
            const isExpanded = button.getAttribute('aria-expanded') === 'true';

            if (isExpanded) {
                // Collapse
                details.style.maxHeight = details.scrollHeight + 'px';
                // Force reflow
                details.offsetHeight;
                details.style.maxHeight = '0';
                details.style.opacity = '0';

                button.setAttribute('aria-expanded', 'false');
                button.textContent = 'More +';

                details.addEventListener('transitionend', function handler() {
                    details.hidden = true;
                    details.style.maxHeight = '';
                    details.style.opacity = '';
                    details.removeEventListener('transitionend', handler);
                }, { once: true });
            } else {
                // Expand
                details.hidden = false;
                details.style.maxHeight = '0';
                details.style.opacity = '0';
                // Force reflow
                details.offsetHeight;
                details.style.maxHeight = details.scrollHeight + 'px';
                details.style.opacity = '1';

                button.setAttribute('aria-expanded', 'true');
                button.textContent = 'Less −';

                details.addEventListener('transitionend', function handler() {
                    details.style.maxHeight = '';
                    details.removeEventListener('transitionend', handler);
                }, { once: true });
            }
        });
    });
})();
