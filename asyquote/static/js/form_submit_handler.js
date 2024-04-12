// form_submit_handler.js

$(document).ready(function () {
    // Handle form submission via AJAX
    $('#create_client_form, #update_client_form, #delete_client_form').submit(function (event) {
        event.preventDefault();
        var form = $(this);
        $.ajax({
            type: form.attr('method'),
            url: form.attr('action'),
            data: form.serialize(),
            success: function (response) {
                if (response.success) {
                    iziToast.success({
                        title: 'Sucesso!',
                        message: response.success,
                    });
                    setTimeout(function () {
                        window.location.reload();
                    }, 800);
                } else if (response.error) {
                    iziToast.error({
                        title: 'Erro!',
                        message: response.error,
                    });
                }
            },
            error: function (xhr, status, error) {
                iziToast.error({
                    title: 'Erro!',
                    message: 'Ocorreu um erro ao processar a solicitação.',
                });
            }
        });
    });
});





function confirmDeleteClient(clientId) {
    document.getElementById('deleteClientId').value = clientId;

    iziToast.question({
        title: 'Confirme',
        message: 'De certeza que pretende eliminar este cliente?<br>Esta ação eliminará o cliente dos registros e todos os projetos associados a este cliente.',
        position: 'topCenter',
        buttons: [
            ['<button>Confirmar</button>', function (instance, toast) {
                instance.hide({transitionOut: 'fadeOut'}, toast, 'button');

                // Submit the form
                document.getElementById('deleteForm').action = `/builder/clients/delete/${clientId}/`;
                document.getElementById('deleteForm').submit();
            }],
            ['<button>Cancelar</button>', function (instance, toast) {
                instance.hide({transitionOut: 'fadeOut'}, toast, 'button');
            }]
        ],
    });
    return false; // Prevent default action
}



function openUpdateModal(clientId) {
    var myModal = new bootstrap.Modal(document.getElementById(`staticClientUpdate${clientId}`));
    myModal.show();
}

function openUpdateModal2(projectId) {
    var myModal2 = new bootstrap.Modal(document.getElementById(`staticProjectUpdate${projectId}`));
    myModal2.show();
}

