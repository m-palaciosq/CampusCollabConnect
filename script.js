$(document).ready(function() {
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
        // can perform more validation like checking username uniqueness, password strength, etc.

        window.location.href = "login.html";
    });
});
