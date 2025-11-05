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