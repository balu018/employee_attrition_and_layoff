document.getElementById('organizationBtn').addEventListener('click', function() {
    toggleForms('organizationSignUpForm', 'organizationLoginForm', 'orgCreateAccount', 'organization');
});

document.getElementById('employeeBtn').addEventListener('click', function() {
    toggleForms('employeeSignUpForm', 'employeeLoginForm', 'empCreateAccount', 'employee');
});

function toggleForms(signUpFormId, loginFormId, createAccountId, userType) {
    const forms = document.querySelectorAll('form');
    const buttons = document.querySelector('.button-container');

    buttons.style.display = 'none';
    forms.forEach(form => form.classList.add('hidden'));
    document.getElementById(loginFormId).classList.remove('hidden');

    const createAccount = document.getElementById(createAccountId).querySelector('span');
    createAccount.addEventListener('click', function() {
        document.getElementById(loginFormId).classList.add('hidden');
        document.getElementById(signUpFormId).classList.remove('hidden');
    });

    document.getElementById(signUpFormId).addEventListener('submit', function(e) {
        e.preventDefault();
        alert('Sign up successful! Now please login.');
        document.getElementById(signUpFormId).classList.add('hidden');
        document.getElementById(loginFormId).classList.remove('hidden');
    });

    document.getElementById(loginFormId).addEventListener('submit', function(e) {
        e.preventDefault();
        if (userType === 'organization') {
            window.location.href = "/org_dashboard";  // Flask route
        } else if (userType === 'employee') {
            window.location.href = "/emp_dashboard";  // Flask route
        }
    });
}

function validateForm(type) {
    const passwordField = type === 'org' ? document.querySelector('#organizationSignUpForm input[type="password"]:first-of-type') : document.querySelector('#employeeSignUpForm input[type="password"]:first-of-type');
    const confirmPasswordField = type === 'org' ? document.getElementById('orgConfirmPassword') : document.getElementById('empConfirmPassword');
    
    const password = passwordField.value;
    const confirmPassword = confirmPasswordField.value;

    // Check if the password is at least 8 characters long and contains different character types
    const passwordCriteria = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$/;

    if (!password.match(passwordCriteria)) {
        alert("Password must be at least 8 characters long and include uppercase letters, lowercase letters, numbers, and special characters.");
        return false;
    }

    // Check if the passwords match
    if (password !== confirmPassword) {
        alert("Passwords do not match.");
        return false;
    }

    return true; // Form is valid
}

