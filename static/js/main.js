// JavaScript per TechShop - Validacions del client

document.addEventListener('DOMContentLoaded', function() {
    // Validació del formulari de checkout
    const checkoutForm = document.getElementById('checkout-form');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', function(e) {
            if (!validateCheckoutForm()) {
                e.preventDefault();
            }
        });
    }

    // Validació dels camps de quantitat
    const quantityInputs = document.querySelectorAll('.quantity-input');
    quantityInputs.forEach(input => {
        input.addEventListener('input', function() {
            validateQuantityInput(this);
        });
    });

    // Carrusel de tendències
    const trendCarousels = document.querySelectorAll('.trend-carousel');
    trendCarousels.forEach(carousel => {
        const slides = carousel.querySelectorAll('.trend-slide');
        const prevButton = carousel.querySelector('.trend-nav-prev');
        const nextButton = carousel.querySelector('.trend-nav-next');

        if (slides.length === 0) {
            if (prevButton) prevButton.setAttribute('disabled', 'true');
            if (nextButton) nextButton.setAttribute('disabled', 'true');
            return;
        }

        let currentIndex = 0;
        slides.forEach((slide, index) => {
            if (index === 0) {
                slide.classList.add('is-active');
                slide.setAttribute('aria-hidden', 'false');
            } else {
                slide.classList.remove('is-active');
                slide.setAttribute('aria-hidden', 'true');
            }
        });

        if (slides.length === 1) {
            if (prevButton) prevButton.setAttribute('disabled', 'true');
            if (nextButton) nextButton.setAttribute('disabled', 'true');
            return;
        }

        const showSlide = (newIndex) => {
            slides[currentIndex].classList.remove('is-active');
            slides[currentIndex].setAttribute('aria-hidden', 'true');

            currentIndex = (newIndex + slides.length) % slides.length;

            slides[currentIndex].classList.add('is-active');
            slides[currentIndex].setAttribute('aria-hidden', 'false');
        };

        if (prevButton) {
            prevButton.addEventListener('click', () => showSlide(currentIndex - 1));
        }

        if (nextButton) {
            nextButton.addEventListener('click', () => showSlide(currentIndex + 1));
        }
    });

    // Galeria de productes: canviar imatge principal segons miniatures
    const productCards = document.querySelectorAll('.product-card');
    productCards.forEach(card => {
        const mainImage = card.querySelector('.product-main-image');
        if (!mainImage) return;

        const defaultSrc = mainImage.getAttribute('data-default') || mainImage.getAttribute('src');
        const thumbs = Array.from(card.querySelectorAll('.product-thumb'));
        const gallery = card.querySelector('.product-gallery');

        if (thumbs.length === 0) {
            return;
        }

        const setActiveThumb = (activeThumb) => {
            thumbs.forEach(thumb => thumb.classList.remove('is-active'));
            if (activeThumb) {
                activeThumb.classList.add('is-active');
            }
        };

        const defaultThumb = thumbs.find(thumb => thumb.dataset.image === defaultSrc) || thumbs[0];

        thumbs.forEach(thumb => {
            const targetSrc = thumb.dataset.image;
            if (!targetSrc) {
                return;
            }

            const showImage = () => {
                mainImage.src = targetSrc;
                setActiveThumb(thumb);
            };

            thumb.addEventListener('mouseenter', showImage);
            thumb.addEventListener('focus', showImage);
        });

        const resetToDefault = () => {
            mainImage.src = defaultSrc;
            setActiveThumb(defaultThumb);
        };

        if (gallery) {
            gallery.addEventListener('mouseleave', resetToDefault);
            gallery.addEventListener('focusout', (event) => {
                if (!gallery.contains(event.relatedTarget)) {
                    resetToDefault();
                }
            });
        }
    });

    // Animació d'afegir al carretó
    const cartIcon = document.getElementById('cart-icon');
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');

    addToCartForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!cartIcon) {
                return;
            }

            const productCard = form.closest('.product-card');
            const productImage = productCard ? productCard.querySelector('.product-main-image') : null;

            if (!productImage) {
                return;
            }

            event.preventDefault();

            const imageRect = productImage.getBoundingClientRect();
            const cartRect = cartIcon.getBoundingClientRect();

            const flyingImage = productImage.cloneNode(true);
            flyingImage.classList.add('flying-image');
            flyingImage.style.left = `${imageRect.left}px`;
            flyingImage.style.top = `${imageRect.top}px`;
            flyingImage.style.width = `${imageRect.width}px`;
            flyingImage.style.height = `${imageRect.height}px`;
            flyingImage.style.opacity = '1';

            document.body.appendChild(flyingImage);

            requestAnimationFrame(() => {
                const translateX = cartRect.left + cartRect.width / 2 - (imageRect.left + imageRect.width / 2);
                const translateY = cartRect.top + cartRect.height / 2 - (imageRect.top + imageRect.height / 2);
                const scale = Math.min(cartRect.width / imageRect.width, cartRect.height / imageRect.height) * 0.65;
                flyingImage.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
                flyingImage.style.opacity = '0';
            });

            cartIcon.classList.add('cart-icon-bump');

            setTimeout(() => {
                flyingImage.remove();
                cartIcon.classList.remove('cart-icon-bump');
            }, 600);

            setTimeout(() => {
                HTMLFormElement.prototype.submit.call(form);
            }, 350);
        });
    });
});

/**
 * Validar el formulari de checkout
 */
function validateCheckoutForm() {
    const username = document.getElementById('username');
    const password = document.getElementById('password');
    const email = document.getElementById('email');
    const address = document.getElementById('address');

    let isValid = true;

    // Validar username
    if (!validateUsername(username.value)) {
        showFieldError(username, 'El nom d\'usuari ha de tenir entre 4 i 20 caràcters i només pot contenir lletres, números i guions baixos');
        isValid = false;
    } else {
        clearFieldError(username);
    }

    // Validar password
    if (!validatePassword(password.value)) {
        showFieldError(password, 'La contrasenya ha de tenir mínim 8 caràcters');
        isValid = false;
    } else {
        clearFieldError(password);
    }

    // Validar email
    if (!validateEmail(email.value)) {
        showFieldError(email, 'Introdueix una adreça de correu vàlida');
        isValid = false;
    } else {
        clearFieldError(email);
    }

    // Validar address
    if (!validateAddress(address.value)) {
        showFieldError(address, 'La adreça és obligatòria');
        isValid = false;
    } else {
        clearFieldError(address);
    }

    return isValid;
}

/**
 * Validar nom d'usuari
 */
function validateUsername(username) {
    const pattern = /^[a-zA-Z0-9_]{4,20}$/;
    return pattern.test(username);
}

/**
 * Validar contrasenya
 */
function validatePassword(password) {
    return password.length >= 8;
}

/**
 * Validar correu electrònic
 */
function validateEmail(email) {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(email);
}

/**
 * Validar adreça
 */
function validateAddress(address) {
    return address.trim().length > 0;
}

/**
 * Validar input de quantitat
 */
function validateQuantityInput(input) {
    const value = parseInt(input.value);
    const min = parseInt(input.getAttribute('min'));
    const max = parseInt(input.getAttribute('max'));

    if (isNaN(value) || value < min || value > max) {
        input.style.borderColor = '#dc3545';
        showFieldError(input, `La quantitat ha d'estar entre ${min} i ${max}`);
        return false;
    } else {
        input.style.borderColor = '#ddd';
        clearFieldError(input);
        return true;
    }
}

/**
 * Mostrar error en un camp
 */
function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    errorDiv.style.color = '#dc3545';
    errorDiv.style.fontSize = '0.9rem';
    errorDiv.style.marginTop = '0.25rem';
    
    field.parentNode.appendChild(errorDiv);
    field.style.borderColor = '#dc3545';
}

/**
 * Netejar error d'un camp
 */
function clearFieldError(field) {
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    field.style.borderColor = '#ddd';
}

/**
 * Mostrar missatge de confirmació
 */
function showConfirmation(message) {
    const flashDiv = document.createElement('div');
    flashDiv.className = 'flash flash-success';
    flashDiv.textContent = message;
    
    const main = document.querySelector('main');
    main.insertBefore(flashDiv, main.firstChild);
    
    // Eliminar el missatge després de 5 segons
    setTimeout(() => {
        flashDiv.remove();
    }, 5000);
}

/**
 * Mostrar missatge d'error
 */
function showError(message) {
    const flashDiv = document.createElement('div');
    flashDiv.className = 'flash flash-error';
    flashDiv.textContent = message;
    
    const main = document.querySelector('main');
    main.insertBefore(flashDiv, main.firstChild);
    
    // Eliminar el missatge després de 5 segons
    setTimeout(() => {
        flashDiv.remove();
    }, 5000);
}