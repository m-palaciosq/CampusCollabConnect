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
$(document).ready(function() {
    $('#create-project-form').submit(function(event) {
        event.preventDefault(); // Prevent form submission

        // Validate form fields
        var title = $('#project-title').val().trim();
        var description = $('#project-description').val().trim();
        var outline = $('#task-outline').val().trim();
        var collaborators = $('#collaborators').val().trim();

        if (title === '' || description === '' || outline === '') {
            alert('Please fill in all required fields.'); // Show error if any label is blank
            return;
        }

        // If all fields are filled, show success message and clear form
        alert('Form submitted successfully!');
        $('#create-project-form')[0].reset(); // Clear form data
    });
});
