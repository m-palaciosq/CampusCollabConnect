$(document).ready(function() {
    $('#loginForm').submit(function(e) {
        e.preventDefault();
        var email = $('#email').val();
        var password = $('#password').val();

        // Test login check
        if (email === 'user' && password === 'pass') {
            alert('Login successful!');
            // Can redirect if needed
        } else {
            $('#error-message').text('Invalid email or password');
        }
    });

    $('#accountCreationForm').submit(function(e) {
        e.preventDefault();
        
        // Fetch input values
        var newEmail = $('#newEmail').val();
        var newPassword = $('#newPassword').val();
        var confirmPassword = $('#confirmPassword').val();

        // Checks
        if(!newEmail.endsWith('@uncg.edu') && newPassword !== confirmPassword){
            $('#creation-error-message').text('Email must end with @uncg.edu\n Passwords do not match');
            return;
        }else if (newPassword !== confirmPassword) {
            $('#creation-error-message').text('Passwords do not match');
            return;
        }else if(!newEmail.endsWith('@uncg.edu')){
            $('#creation-error-message').text('Email must end with @uncg.edu');
            return;
        }
        // Here you can perform additional validation like checking username uniqueness, password strength, etc.

        // If all validation passes, you can proceed with account creation
        alert('Account created successfully!');
        // Can redirect the user to the login page after successful account creation
    });
});
