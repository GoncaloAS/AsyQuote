 document.addEventListener('DOMContentLoaded', function() {
        var form = document.getElementById('create_project_form_prevention');
        var submitButton = document.getElementById('create_project_submit');

        form.addEventListener('submit', function(event) {
            // Disable the submit button to prevent multiple submissions
            submitButton.disabled = true;

            // Re-enable the submit button after 5 seconds (5000 milliseconds)
            setTimeout(function() {
                submitButton.disabled = false;
            }, 5000);
        });
    });
