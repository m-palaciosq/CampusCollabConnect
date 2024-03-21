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
