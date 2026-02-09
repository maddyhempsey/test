// Mobile navigation toggle
const navToggle = document.querySelector('.nav-toggle');
const nav = document.querySelector('.nav');

navToggle.addEventListener('click', () => {
    nav.classList.toggle('open');
});

// Close mobile nav when a link is clicked
nav.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
        nav.classList.remove('open');
    });
});

// Contact form handling
const form = document.getElementById('contactForm');

form.addEventListener('submit', (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const name = formData.get('name');

    // Replace form with success message
    form.innerHTML = '<div class="form-success">Tak for din besked, ' +
        name.split('<').join('&lt;') +
        '! Vi vender tilbage hurtigst muligt.</div>';
});

// Header shadow on scroll
const header = document.querySelector('.header');

window.addEventListener('scroll', () => {
    if (window.scrollY > 10) {
        header.style.boxShadow = '0 1px 8px rgba(0,0,0,0.08)';
    } else {
        header.style.boxShadow = 'none';
    }
});
