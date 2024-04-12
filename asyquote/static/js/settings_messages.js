let toastVisible = false;
window.addEventListener('DOMContentLoaded', function () {
    const message = "{% translate 'Deseja mesmo remover este email da sua conta?' %}";
    const actions = document.getElementsByName('action_remove');
    if (actions.length) {
        actions[0].addEventListener("click", function (e) {
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    }
    Array.from(document.getElementsByClassName('form-group')).forEach(x => x.classList.remove('row'));
});

document.addEventListener('DOMContentLoaded', function () {

    document.getElementById('password_change_form').addEventListener('submit', function (event) {
        event.preventDefault();
        let formData = new FormData(this);
        let form = this;
        $.ajax({
            url: form.action,
            type: form.method,
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                if (response.success) {
                    iziToast.success({
                        title: 'Success',
                        message: response.message,
                        position: 'bottomRight'
                    });
                    form.reset();
                } else {
                    iziToast.error({
                        title: 'Error',
                        message: response.message,
                        position: 'bottomRight'
                    });
                }
            },
            error: function (xhr, status, error) {
                console.error('Form submission failed:', error);
            }
        });
    });

    document.getElementById('marketing_preferences_form').addEventListener('submit', function (event) {
        event.preventDefault();
        if (!toastVisible) {
            iziToast.success({
                title: 'Sucesso',
                message: 'Preferências de marketing mudadas com sucesso',
                position: 'bottomRight',
                onOpening: function () {
                    toastVisible = true;
                },
                onClosed: function () {
                    toastVisible = false;
                }
            });
        }
        let formData = new FormData(this);

        // Submit form data asynchronously using AJAX
        $.ajax({
            url: this.action,
            type: this.method,
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                // Handle successful form submission
                console.log('Form submitted successfully');
            },
            error: function (xhr, status, error) {
                // Handle errors
                console.error('Form submission failed:', error);
            }
        });


    });

});
