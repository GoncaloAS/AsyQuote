$(document).ready(function () {
    let counter = 1;
    const saveQuoteUrl = $("#quote-url-dropdown").attr("data-quote-url");
    function saveQuote(action, key) {
        $.ajax({
            url: saveQuoteUrl,
            type: 'GET',
            data: {
                action: action,
                key: key,
                csrfmiddlewaretoken: '{{ csrf_token }}',

            },
            success: function (data) {
                // Handle success response
                console.log(data);
            },
            error: function (xhr, textStatus, errorThrown) {
                // Handle error
                console.error(xhr.responseText);
            }
        });
    }

    $('.add-section').click(function (e) {
        e.preventDefault();
        var projectKey = $(this).data('key');
        saveQuote('add-section', projectKey);
        $('#myForm').append(
            '<input type="text" name="section" placeholder="Nova secção">' +
            '<div class="service-fields">' +
            '<input class="services-form" type="text" name="service" placeholder="Novo serviço/produto">' +
            '<input class="prices-form" type="text" name="quantity" placeholder="Quantidade">' +
            '</div>' +
            '<div class="price-fields">' +
            '<input class="prices-form" type="text" name="description" placeholder="Descrição despesas">' +
            '<input class="prices-form color-cost" type="number" min="0" name="price" placeholder="Custo" id="input-custo-' + counter + '" onkeydown="preventNegativeInput(event, this);">' +
            '<input class="prices-form color-cobrado" type="number" min="0" name="price" placeholder="Cobrado" id="input-cobrado-' + counter + '" onkeydown="preventNegativeInput(event, this); addPercentageCost(event, this)">' +
            '</div>'
        );
        document.getElementById('add-service').style.display = 'block';
        document.getElementById('add-section').style.display = 'block';
        document.getElementById('add-price').style.display = 'block';
        scrollFormToBottom();
        counter++;
    });

    $('.add-service').click(function (e) {
        var projectKey = $(this).data('key');
        saveQuote('add-service', projectKey);
        $('#myForm').append(
            '<div class="service-fields">' +
            '<input class="services-form" type="text" name="service" placeholder="Novo serviço/produto">' +
            '<input class="prices-form" type="text" name="quantity" placeholder="Quantidade">' +
            '</div>' +
            '<div class="price-fields">' +
            '<input class="prices-form" type="text" name="description" placeholder="Descrição despesas">' +
            '<input class="prices-form color-cost" type="number" min="0" name="price" placeholder="Custo" id="input-custo-' + counter + '" onkeydown="preventNegativeInput(event, this);">' +
            '<input class="prices-form color-cobrado" type="number" min="0" name="price" placeholder="Cobrado" id="input-cobrado-' + counter + '" onkeydown="preventNegativeInput(event, this); addPercentageCost(event, this)">' +
            '</div>'
        )
        document.getElementById('add-section').style.display = 'block';
        document.getElementById('add-price').style.display = 'block';
        scrollFormToBottom();
        counter++;
    });

    $('.add-price').click(function (e) {
        var projectKey = $(this).data('key');
        saveQuote('add-price', projectKey);
        $('#myForm').append(
            '<div class="price-fields">' +
            '<input class="prices-form" type="text" name="description" placeholder="Descrição despesas">' +
            '<input class="prices-form color-cost" type="number" min="0" name="price" placeholder="Custo" id="input-custo-' + counter + '" onkeydown="preventNegativeInput(event, this);">' +
            '<input class="prices-form color-cobrado" type="number" min="0" name="price" placeholder="Cobrado" id="input-cobrado-' + counter + '" onkeydown="preventNegativeInput(event, this); addPercentageCost(event, this)">' +
            '</div>'
        );
        scrollFormToBottom();
        counter++;
    });
});

function preventNegativeInput(event, input) {
    if (event.key === '-' || event.key === '+') {
        event.preventDefault();
        input.value = '';
    }
}

function addPercentageCost(event, input) {
    if (event.key === '%') {
        event.preventDefault();
        var inputId = 'input-custo-' + input.id.split('-')[2];
        const value = parseInt(document.getElementById(inputId).value)
        const divider = parseFloat(input.value / 100)
        input.value = value + Math.round((value * divider));

    }
}

function confirmDeleteProject(projectId) {
    document.getElementById('deleteProjectId').value = projectId;

    iziToast.question({
        title: 'Confirme',
        message: 'Tem a certeza de que deseja excluir este projeto? <br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' +
            '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Esta ação será irreversível.',
        position: 'topCenter',
        buttons: [
            ['<button>Confirmar</button>', function (instance, toast) {
                instance.hide({transitionOut: 'fadeOut'}, toast, 'button');

                // Submit the form
                document.getElementById('deleteProjectForm').action = `/builder/projects/delete/${projectId}/`;
                document.getElementById('deleteProjectForm').submit();
            }],
            ['<button>Cancelar</button>', function (instance, toast) {
                instance.hide({transitionOut: 'fadeOut'}, toast, 'button');
            }]
        ],
    });
    return false;
}

function previewImage(input, projectId) {
    var preview = document.getElementById('imagePreview' + projectId);
    var label = document.querySelector('.custom-file-label');
    var file = input.files[0];
    var reader = new FileReader();

    reader.onloadend = function () {
        preview.src = reader.result;
        const file_name = file.name
        const maxLength = 50;
        if (file_name.length > maxLength) {
            label.textContent = file_name.substring(0, maxLength) + '...';
        } else {
            label.textContent = file_name;
        }
    }

    if (file) {
        reader.readAsDataURL(file);
    } else {
        preview.src = "";
    }
}

function previewImageCreate(input) {
    var preview = document.getElementById('imagePreviewCreate')
    var label = document.querySelector('.custom-file-label');
    preview.style.display = 'block';
    var file = input.files[0];
    var reader = new FileReader();

    reader.onloadend = function () {
        preview.src = reader.result;
        const file_name = file.name
        const maxLength = 50;
        if (file_name.length > maxLength) {
            label.textContent = file_name.substring(0, maxLength) + '...';
        } else {
            label.textContent = file_name;
        }
    }

    if (file) {
        reader.readAsDataURL(file);
    }
}


$(document).ready(function () {
    // Handle form submission via AJAX
    $('#update_project_form').submit(function (event) {
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
                    message: 'Ocorreu um erro ao processar a solicitação. Verifique se a informação está coretamente preenchida.',
                });
            }
        });
    });
});

function scrollFormToBottom() {
    window.scrollBy(0, 10000);
}
