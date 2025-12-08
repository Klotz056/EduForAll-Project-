// Authentication Modal Handler
document.addEventListener('DOMContentLoaded', function() {
    const authModal = new bootstrap.Modal(document.getElementById('authModal'));
    const roleRadios = document.querySelectorAll('input[name="role"]');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const formLogin = document.getElementById('form-login');
    const formRegister = document.getElementById('form-register');
    const switchToRegister = document.getElementById('switchToRegister');
    const switchToLogin = document.getElementById('switchToLogin');
    const authMessage = document.getElementById('authMessage');
    const mentorExpertiseField = document.getElementById('mentor_expertise');

    // Store current role
    let currentRole = 'student';

    // Role selection change
    roleRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            currentRole = this.value;
            
            // Show/hide mentor expertise field
            if (currentRole === 'mentor') {
                mentorExpertiseField.style.display = 'block';
            } else {
                mentorExpertiseField.style.display = 'none';
            }

            // Reset forms when role changes
            formLogin.reset();
            formRegister.reset();
            hideMessage();
        });
    });

    // Switch between login and register
    switchToRegister.addEventListener('click', function() {
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
        formLogin.reset();
        hideMessage();
    });

    switchToLogin.addEventListener('click', function() {
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
        formRegister.reset();
        hideMessage();
    });

    // Show message helper
    function showMessage(message, isError = false) {
        authMessage.innerHTML = '';
        authMessage.className = isError ? 'alert alert-danger' : 'alert alert-success';
        authMessage.textContent = message;
        authMessage.style.display = 'block';
    }

    function hideMessage() {
        authMessage.style.display = 'none';
    }

    // Login form submission
    formLogin.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('login_email').value.trim();
        const password = document.getElementById('login_password').value;

        if (!email || !password) {
            showMessage('Please fill in all fields', true);
            return;
        }

        try {
            // Check if user exists
            const checkResponse = await fetch('/schoolApp/api/check-user/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    role: currentRole
                })
            });

            const checkData = await checkResponse.json();

            if (!checkData.exists) {
                showMessage(`No ${currentRole} account found with this email. Please register first.`, true);
                return;
            }

            // Attempt login
            const loginResponse = await fetch('/schoolApp/api/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                    role: currentRole
                })
            });

            const loginData = await loginResponse.json();

            if (loginData.success) {
                showMessage(`Welcome back, ${loginData.user_name}!`);
                
                // Store user session (in browser storage or cookies)
                sessionStorage.setItem('user_id', loginData.user_id);
                sessionStorage.setItem('user_name', loginData.user_name);
                sessionStorage.setItem('user_email', loginData.email);
                sessionStorage.setItem('user_role', loginData.role);
                
                // Close modal after 1 second
                setTimeout(() => {
                    authModal.hide();
                    // Redirect or perform action
                    window.location.href = '/';
                }, 1000);
            } else {
                showMessage(loginData.error || 'Login failed', true);
            }
        } catch (error) {
            console.error('Error:', error);
            showMessage('An error occurred during login', true);
        }
    });

    // Register form submission
    formRegister.addEventListener('submit', async function(e) {
        e.preventDefault();

        const firstName = document.getElementById('register_first_name').value.trim();
        const lastName = document.getElementById('register_last_name').value.trim();
        const email = document.getElementById('register_email').value.trim();
        const phone = document.getElementById('register_phone').value.trim();
        const password = document.getElementById('register_password').value;
        const confirmPassword = document.getElementById('register_confirm_password').value;
        const expertise = document.getElementById('register_expertise').value.trim();

        // Validation
        if (!firstName || !lastName || !email || !phone || !password) {
            showMessage('Please fill in all required fields', true);
            return;
        }

        if (password !== confirmPassword) {
            showMessage('Passwords do not match', true);
            return;
        }

        if (password.length < 6) {
            showMessage('Password must be at least 6 characters long', true);
            return;
        }

        try {
            const registerData = {
                first_name: firstName,
                last_name: lastName,
                email: email,
                phone_number: phone,
                password: password,
                role: currentRole
            };

            if (currentRole === 'mentor' && expertise) {
                registerData.expertise = expertise;
            }

            const registerResponse = await fetch('/schoolApp/api/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(registerData)
            });

            const registerData_response = await registerResponse.json();

            if (registerData_response.success) {
                showMessage(registerData_response.message);
                
                // Store user session
                sessionStorage.setItem('user_id', registerData_response.user_id);
                sessionStorage.setItem('user_name', `${firstName} ${lastName}`);
                sessionStorage.setItem('user_email', email);
                sessionStorage.setItem('user_role', registerData_response.role);
                
                // Close modal after 1 second
                setTimeout(() => {
                    authModal.hide();
                    window.location.href = '/';
                }, 1000);
            } else {
                showMessage(registerData_response.error || 'Registration failed', true);
            }
        } catch (error) {
            console.error('Error:', error);
            showMessage('An error occurred during registration', true);
        }
    });

    // Expose modal to global scope for "Join Now" buttons
    window.openAuthModal = function() {
        authModal.show();
    };
});
