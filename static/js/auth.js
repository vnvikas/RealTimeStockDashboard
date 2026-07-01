/**
 * Authentication JavaScript for Stock Market Dashboard
 * Handles login, registration, and password management
 */

// ============================================
// Registration Form Validation
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            validateRegistrationForm(this);
        });
        
        // Real-time validation
        const passwordInput = document.getElementById('password');
        if (passwordInput) {
            passwordInput.addEventListener('input', function() {
                validatePasswordStrength(this.value);
            });
        }
        
        // Check username availability
        const usernameInput = document.getElementById('username');
        if (usernameInput) {
            usernameInput.addEventListener('blur', function() {
                checkUsernameAvailability(this.value);
            });
        }
        
        // Check email availability
        const emailInput = document.getElementById('email');
        if (emailInput) {
            emailInput.addEventListener('blur', function() {
                checkEmailAvailability(this.value);
            });
        }
    }
});

function validateRegistrationForm(form) {
    const username = form.querySelector('#username').value.trim();
    const email = form.querySelector('#email').value.trim();
    const fullName = form.querySelector('#full_name').value.trim();
    const password = form.querySelector('#password').value;
    const confirmPassword = form.querySelector('#confirm_password').value;
    const mobile = form.querySelector('#mobile') ? form.querySelector('#mobile').value.trim() : '';
    
    let errors = [];
    
    // Validate username
    if (!username) {
        errors.push('Username is required.');
    } else if (!/^[a-zA-Z0-9_]{3,50}$/.test(username)) {
        errors.push('Username must be 3-50 characters and contain only letters, numbers, and underscores.');
    }
    
    // Validate email
    if (!email) {
        errors.push('Email is required.');
    } else if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)) {
        errors.push('Please enter a valid email address.');
    }
    
    // Validate full name
    if (!fullName) {
        errors.push('Full name is required.');
    }
    
    // Validate password
    if (!password) {
        errors.push('Password is required.');
    } else {
        const passwordStrength = validatePasswordStrength(password);
        if (!passwordStrength.isValid) {
            errors.push(passwordStrength.message);
        }
    }
    
    // Validate password confirmation
    if (password && password !== confirmPassword) {
        errors.push('Passwords do not match.');
    }
    
    // Validate mobile (optional)
    if (mobile && !/^\+?[0-9]{10,15}$/.test(mobile)) {
        errors.push('Please enter a valid phone number.');
    }
    
    if (errors.length > 0) {
        showErrors(errors);
        return false;
    }
    
    // Submit form
    form.submit();
}

function validatePasswordStrength(password) {
    const result = { isValid: true, message: '' };
    
    if (password.length < 8) {
        result.isValid = false;
        result.message = 'Password must be at least 8 characters long.';
    } else if (!/[A-Z]/.test(password)) {
        result.isValid = false;
        result.message = 'Password must contain at least one uppercase letter.';
    } else if (!/[a-z]/.test(password)) {
        result.isValid = false;
        result.message = 'Password must contain at least one lowercase letter.';
    } else if (!/[0-9]/.test(password)) {
        result.isValid = false;
        result.message = 'Password must contain at least one number.';
    } else if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
        result.isValid = false;
        result.message = 'Password must contain at least one special character.';
    }
    
    // Update password strength indicator
    updatePasswordStrengthIndicator(password);
    
    return result;
}

function updatePasswordStrengthIndicator(password) {
    const indicator = document.getElementById('passwordStrength');
    if (!indicator) return;
    
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++;
    
    const levels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
    const colors = ['#dc3545', '#dc3545', '#ffc107', '#28a745', '#28a745'];
    
    const percentage = (strength / 5) * 100;
    indicator.style.width = percentage + '%';
    indicator.className = 'progress-bar';
    indicator.style.backgroundColor = colors[strength] || '#dc3545';
    indicator.textContent = levels[strength] || 'Very Weak';
    indicator.setAttribute('aria-valuenow', strength);
}

function checkUsernameAvailability(username) {
    if (username.length < 3) return;
    
    const feedback = document.getElementById('usernameFeedback');
    if (!feedback) return;
    
    fetch('/auth/check-availability', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ field: 'username', value: username })
    })
    .then(response => response.json())
    .then(data => {
        if (data.available) {
            feedback.className = 'valid-feedback d-block';
            feedback.textContent = 'Username is available.';
            document.querySelector('#username').classList.add('is-valid');
            document.querySelector('#username').classList.remove('is-invalid');
        } else {
            feedback.className = 'invalid-feedback d-block';
            feedback.textContent = 'Username is already taken.';
            document.querySelector('#username').classList.add('is-invalid');
            document.querySelector('#username').classList.remove('is-valid');
        }
    })
    .catch(error => {
        console.error('Error checking username:', error);
    });
}

function checkEmailAvailability(email) {
    if (!email || !/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)) return;
    
    const feedback = document.getElementById('emailFeedback');
    if (!feedback) return;
    
    fetch('/auth/check-availability', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ field: 'email', value: email })
    })
    .then(response => response.json())
    .then(data => {
        if (data.available) {
            feedback.className = 'valid-feedback d-block';
            feedback.textContent = 'Email is available.';
            document.querySelector('#email').classList.add('is-valid');
            document.querySelector('#email').classList.remove('is-invalid');
        } else {
            feedback.className = 'invalid-feedback d-block';
            feedback.textContent = 'Email is already registered.';
            document.querySelector('#email').classList.add('is-invalid');
            document.querySelector('#email').classList.remove('is-valid');
        }
    })
    .catch(error => {
        console.error('Error checking email:', error);
    });
}

function showErrors(errors) {
    const errorContainer = document.getElementById('errorContainer');
    if (!errorContainer) return;
    
    errorContainer.innerHTML = '';
    errors.forEach(function(error) {
        const div = document.createElement('div');
        div.className = 'alert alert-danger alert-dismissible fade show';
        div.innerHTML = `
            ${error}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        errorContainer.appendChild(div);
    });
    errorContainer.style.display = 'block';
}

// ============================================
// Login Form
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            // Form will submit normally
        });
    }
    
    // Show/hide password
    const togglePassword = document.getElementById('togglePassword');
    if (togglePassword) {
        togglePassword.addEventListener('click', function() {
            const passwordInput = document.getElementById('password');
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            this.querySelector('i').className = type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash';
        });
    }
});

// ============================================
// Forgot Password
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    const forgotForm = document.getElementById('forgotPasswordForm');
    if (forgotForm) {
        forgotForm.addEventListener('submit', function(e) {
            const email = this.querySelector('#email').value.trim();
            if (!email || !/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)) {
                e.preventDefault();
                showToast('Please enter a valid email address.', 'danger');
                return false;
            }
        });
    }
});

// ============================================
// Reset Password
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    const resetForm = document.getElementById('resetPasswordForm');
    if (resetForm) {
        resetForm.addEventListener('submit', function(e) {
            e.preventDefault();
            validateResetPassword(this);
        });
        
        const passwordInput = document.getElementById('password');
        if (passwordInput) {
            passwordInput.addEventListener('input', function() {
                validatePasswordStrength(this.value);
            });
        }
    }
});

function validateResetPassword(form) {
    const password = form.querySelector('#password').value;
    const confirmPassword = form.querySelector('#confirm_password').value;
    
    let errors = [];
    
    const strength = validatePasswordStrength(password);
    if (!strength.isValid) {
        errors.push(strength.message);
    }
    
    if (password !== confirmPassword) {
        errors.push('Passwords do not match.');
    }
    
    if (errors.length > 0) {
        showErrors(errors);
        return false;
    }
    
    form.submit();
}