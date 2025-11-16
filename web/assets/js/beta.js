/**
 * Beta Application Form Handler
 */

// API endpoint (update for production)
const API_BASE_URL = '/api/v1';

// Form submission handler
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('betaApplicationForm');
    const successMessage = document.getElementById('successMessage');

    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();

            // Disable submit button
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting...';

            try {
                // Collect form data
                const formData = new FormData(form);
                const applicationData = {
                    email: formData.get('email'),
                    name: formData.get('name'),
                    phone: formData.get('phone') || null,
                    telegram: formData.get('telegram') || null,
                    trading_experience: parseInt(formData.get('trading_experience')),
                    platforms_used: formData.getAll('platforms'),
                    primary_pairs: formData.getAll('pairs'),
                    availability: parseInt(formData.get('availability')),
                    feedback_commitment: formData.get('feedback_commitment') === 'on',
                    why_join: formData.get('why_join'),
                    expectations: formData.get('expectations') || null,
                };

                // Validate required fields
                if (!applicationData.email || !applicationData.name) {
                    throw new Error('Please fill in all required fields');
                }

                if (applicationData.platforms_used.length === 0) {
                    throw new Error('Please select at least one trading platform');
                }

                if (applicationData.primary_pairs.length === 0) {
                    throw new Error('Please select at least one currency pair');
                }

                // Submit to API
                const response = await fetch(`${API_BASE_URL}/beta/apply`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(applicationData),
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.message || 'Submission failed');
                }

                const result = await response.json();

                // Show success message
                form.style.display = 'none';
                successMessage.style.display = 'block';

                // Scroll to success message
                successMessage.scrollIntoView({ behavior: 'smooth' });

                // Track conversion
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'beta_application_submit', {
                        'event_category': 'engagement',
                        'event_label': result.status,
                    });
                }

                // Send to Kluster for tracking (if available)
                if (typeof kluster !== 'undefined') {
                    kluster.track('beta_application', {
                        status: result.status,
                        score: result.score,
                    });
                }

            } catch (error) {
                console.error('Submission error:', error);
                alert('Error: ' + error.message + '\\n\\nPlease try again or contact support@quantumtrading.ai');

                // Re-enable submit button
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }

    // Form validation helpers
    const emailInput = document.getElementById('email');
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            const email = this.value.trim();
            if (email && !isValidEmail(email)) {
                this.setCustomValidity('Please enter a valid email address');
            } else {
                this.setCustomValidity('');
            }
        });
    }

    // Phone number formatting (South African format)
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            let value = this.value.replace(/\D/g, '');
            if (value.startsWith('27')) {
                value = '+' + value;
            } else if (value.startsWith('0')) {
                value = '+27' + value.substring(1);
            }
            this.value = value;
        });
    }

    // Telegram username validation
    const telegramInput = document.getElementById('telegram');
    if (telegramInput) {
        telegramInput.addEventListener('input', function() {
            let value = this.value.trim();
            if (value && !value.startsWith('@')) {
                this.value = '@' + value;
            }
        });
    }
});

// Helper functions
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href === '#') return;

        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Track page view
if (typeof gtag !== 'undefined') {
    gtag('event', 'page_view', {
        'page_title': 'Beta Program',
        'page_location': window.location.href,
    });
}
