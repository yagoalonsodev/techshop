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

    // Gestió del checkout: mostrar/ocultar seccions segons l'elecció
    const btnLogin = document.getElementById('btn-login');
    const btnGuest = document.getElementById('btn-guest');
    const btnBackFromLogin = document.getElementById('btn-back-from-login');
    const btnBackFromGuest = document.getElementById('btn-back-from-guest');
    const checkoutChoice = document.getElementById('checkout-choice');
    const loginSection = document.getElementById('login-section');
    const guestSection = document.getElementById('guest-section');

    if (btnLogin && checkoutChoice && loginSection) {
        btnLogin.addEventListener('click', function() {
            checkoutChoice.style.display = 'none';
            loginSection.style.display = 'block';
        });
    }

    if (btnGuest && checkoutChoice && guestSection) {
        btnGuest.addEventListener('click', function() {
            checkoutChoice.style.display = 'none';
            guestSection.style.display = 'block';
        });
    }

    if (btnBackFromLogin && checkoutChoice && loginSection) {
        btnBackFromLogin.addEventListener('click', function() {
            loginSection.style.display = 'none';
            checkoutChoice.style.display = 'block';
        });
    }

    if (btnBackFromGuest && checkoutChoice && guestSection) {
        btnBackFromGuest.addEventListener('click', function() {
            guestSection.style.display = 'none';
            checkoutChoice.style.display = 'block';
        });
    }
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

/**
 * Validar DNI espanyol
 * Format: 8 números seguits d'una lletra de control
 */
function validarDNI(dni) {
    // Formato
    if (!/^\d{8}[A-Za-z]$/.test(dni)) return false;
    
    const letras = "TRWAGMYFPDXBNJZSQVHLCKE";
    const numero = parseInt(dni.substring(0, 8), 10);
    const letra = dni.charAt(8).toUpperCase();
    const letraCorrecta = letras[numero % 23];
    
    return letra === letraCorrecta;
}

/**
 * Validar NIE espanyol
 * Format: X/Y/Z + 7 números + lletra de control
 */
function validarNIE(nie) {
    // Formato
    if (!/^[XYZ]\d{7}[A-Za-z]$/.test(nie)) return false;
    
    const letras = "TRWAGMYFPDXBNJZSQVHLCKE";
    const inicial = nie.charAt(0).toUpperCase();
    const letra = nie.slice(-1).toUpperCase();
    
    // Convertir inicial
    const valores = { X: 0, Y: 1, Z: 2 };
    const numero = valores[inicial] + nie.substring(1, 8);
    const letraCorrecta = letras[numero % 23];
    
    return letra === letraCorrecta;
}

/**
 * Validar CIF espanyol
 * Format: Lletra + 7 números + caràcter de control
 */
function validarCIF(cif) {
    if (!/^[ABCDEFGHJKLMNPQRSUVW]\d{7}[0-9A-J]$/.test(cif)) return false;
    
    const letraInicial = cif.charAt(0).toUpperCase();
    const digitos = cif.substring(1, 8);
    const controlChar = cif.charAt(8).toUpperCase();
    
    let sumaPares = 0;
    let sumaImpares = 0;
    
    for (let i = 0; i < digitos.length; i++) {
        const n = parseInt(digitos.charAt(i), 10);
        if ((i + 1) % 2 === 0) {
            sumaPares += n;
        } else {
            let mult = n * 2;
            sumaImpares += Math.floor(mult / 10) + (mult % 10);
        }
    }
    
    const suma = sumaPares + sumaImpares;
    const unidad = suma % 10;
    let controlNum = (10 - unidad) % 10;
    const tablaControl = "JABCDEFGHI";
    const controlLetra = tablaControl[controlNum];
    
    // Reglas según letra inicial
    if ("ABEH".includes(letraInicial)) {
        return controlChar === String(controlNum);
    }
    if ("KPQS".includes(letraInicial)) {
        return controlChar === controlLetra;
    }
    
    // Otros casos: ambos son válidos
    return controlChar === String(controlNum) || controlChar === controlLetra;
}

/**
 * Validar DNI o NIE (per usuaris individuals)
 */
function validarDNI_NIE(dni) {
    if (!dni || dni.trim().length === 0) return false;
    const dniUpper = dni.trim().toUpperCase();
    
    // Si comienza con X, Y o Z, es NIE
    if (/^[XYZ]/.test(dniUpper)) {
        return validarNIE(dniUpper);
    }
    // Si no, es DNI
    return validarDNI(dniUpper);
}

/**
 * Validar CIF (per empreses)
 */
function validarCIF_NIF(nif) {
    if (!nif || nif.trim().length === 0) return false;
    return validarCIF(nif.trim().toUpperCase());
}