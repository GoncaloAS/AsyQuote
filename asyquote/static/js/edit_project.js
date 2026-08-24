$(document).ready(function () {
  let counter = 1;
  const saveQuoteUrl = $('#quote-url-dropdown').attr('data-quote-url');

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
        replaceForm(data.form_html);
        addChangeSectionEventListeners();
      },
      error: function (xhr, textStatus, errorThrown) {
        console.error(xhr.responseText);
      },
    });
  }

  $('.add-section').click(function (e) {
    e.preventDefault();
    var projectKey = $(this).data('key');
    saveQuote('add-section', projectKey);
    scrollFormToBottom();
    counter++;
  });

  $('.add-service').click(function (e) {
    var projectKey = $(this).data('key');
    saveQuote('add-service', projectKey);
    scrollFormToBottom();
    counter++;
  });

  $('.add-price').click(function (e) {
    var projectKey = $(this).data('key');
    saveQuote('add-price', projectKey);
    scrollFormToBottom();
    counter++;
  });
});

// region Section 1: erase, delete, prevent negative, add percentage

function preventNegativeInput(event, input) {
  const regex = /^[\d,.]*$/;

  if (!regex.test(input.value)) {
    event.preventDefault();
    if (input.value !== '') {
      input.value = '';
    }
  }
}

function addPercentageCost(event, input) {
  if (event.key === '%') {
    event.preventDefault();
    var inputId = 'input-custo-' + input.id.split('-')[2];
    const value = parseInt(document.getElementById(inputId).value);
    const divider = parseFloat(input.value / 100);
    input.value = value + value * divider;
  }
}

function eraseSection(input) {
  let inputId = 'input-section-' + input;
  document.getElementById(inputId).value = '';
  let inputElement = document.getElementById(inputId);
  inputElement.dispatchEvent(new Event('change'));
  setTimeout(() => {
    inputElement.removeEventListener('change', handleSectionChange);
  }, 100);
}

function eraseService(input) {
  let inputId = 'input-service-' + input;
  let inputId2 = 'input-quantity-' + input;
  document.getElementById(inputId).value = '';
  document.getElementById(inputId2).value = '';
  let inputElement = document.getElementById(inputId);
  let inputElement2 = document.getElementById(inputId2);
  setTimeout(() => {
    inputElement.dispatchEvent(new Event('change'));
    setTimeout(() => {
      inputElement2.dispatchEvent(new Event('change'));
      setTimeout(() => {
        inputElement.removeEventListener('change', handleServiceChange);
        inputElement2.removeEventListener('change', handleServiceChange);
      }, 100);
    }, 100);
  }, 100);
}

function erasePrice(input) {
  let inputId = 'input-descricao-' + input;
  let inputId2 = 'input-custo-' + input;
  let inputId3 = 'input-cobrado-' + input;

  document.getElementById(inputId).value = '';
  document.getElementById(inputId2).value = 0;
  document.getElementById(inputId3).value = 0;

  let inputElement = document.getElementById(inputId);
  let inputElement2 = document.getElementById(inputId2);
  let inputElement3 = document.getElementById(inputId3);

  setTimeout(() => {
    inputElement.dispatchEvent(new Event('change'));
  }, 0);

  setTimeout(() => {
    inputElement2.dispatchEvent(new Event('change'));
  }, 100);

  setTimeout(() => {
    inputElement3.dispatchEvent(new Event('change'));
  }, 200);

  setTimeout(() => {
    inputElement.removeEventListener('change', handlePriceChange);
    inputElement2.removeEventListener('change', handlePriceChange);
    inputElement3.removeEventListener('change', handlePriceChange);
  }, 300);
}

function deleteSection(input) {
  let inputMinus = parseInt(input) - 1;
  let inputPlus = parseInt(input) + 1;
  let sectionFields = document.querySelectorAll(
    '[data-section-identifier="' + input + '"]',
  );
  let sectionFieldMinus = document.querySelectorAll(
    '[data-section-identifier="' + inputMinus + '"]',
  );
  let sectionFieldPlus = document.querySelectorAll(
    '[data-section-identifier="' + inputPlus + '"]',
  );
  if (sectionFieldMinus.length > 0 || sectionFieldPlus.length > 0) {
    sectionFields.forEach((section) => {
      section.remove();
    });
  }
  deleteField('drop-section', key, input, 0, 0);
}

function deleteService(input, input2) {
  let inputMinus = parseInt(input2) - 1;
  let inputPlus = parseInt(input2) + 1;
  let serviceFields = document.querySelectorAll(
    '[data-section-identifier="' +
      input +
      '"][data-service-identifier="' +
      input2 +
      '"]',
  );
  let serviceFieldPlus = document.querySelectorAll(
    '[data-section-identifier="' +
      input +
      '"][data-service-identifier="' +
      inputPlus +
      '"]',
  );
  let serviceFieldMinus = document.querySelectorAll(
    '[data-section-identifier="' +
      input +
      '"][data-service-identifier="' +
      inputMinus +
      '"]',
  );
  if (serviceFieldMinus.length > 0 || serviceFieldPlus.length > 0) {
    serviceFields.forEach((service) => {
      service.remove();
    });
  }
  deleteField('drop-service', key, input, input2, 0);
}

function deletePrice(input, input2, input3) {
  let inputMinus = parseInt(input3) - 1;
  let inputPlus = parseInt(input3) + 1;
  let priceFields = document.querySelectorAll(
    '[data-section-identifier="' +
      input +
      '"][data-service-identifier="' +
      input2 +
      '"][data-price-identifier="' +
      input3 +
      '"]',
  );
  let priceFieldPlus = document.querySelectorAll(
    '[data-section-identifier="' +
      input +
      '"][data-service-identifier="' +
      input2 +
      '"][data-price-identifier="' +
      inputPlus +
      '"]',
  );
  let priceFieldMinus = document.querySelectorAll(
    '[data-section-identifier="' +
      input +
      '"][data-service-identifier="' +
      input2 +
      '"][data-price-identifier="' +
      inputMinus +
      '"]',
  );
  if (priceFieldMinus.length > 0 || priceFieldPlus.length > 0) {
    priceFields.forEach((price) => {
      price.remove();
    });
  }
  deleteField('drop-price', key, input, input2, input3);
}

// endregion
function addSection(input) {
  let nextSection = parseInt(input) + 1;
  createField('add-section', key, input, 0, 0, nextSection);
}
function addService(input, input2) {
  let nextService = parseInt(input2) + 1;
  createField('add-service', key, input, input2, 0, nextService);
}

function addPrice(input, input2, input3) {
  let nextPrice = parseInt(input3) + 1;
  createField('add-price', key, input, input2, input3, nextPrice);
}

// Replacing the whole form's innerHTML destroys and rebuilds every row, which
// drops the page height to nothing for an instant and leaves the browser scrolled
// back to the top. Pin the offset across the swap.
function replaceForm(html) {
  if (typeof html !== 'string' || html.length === 0) {
    return false;
  }
  const offset = window.scrollY;
  $('#myForm').html(html);
  window.scrollTo({ top: offset, behavior: 'instant' });
  return true;
}

function reportQuoteError(message) {
  if (!message) {
    return;
  }
  if (typeof iziToast !== 'undefined') {
    iziToast.error({
      title: 'Erro!',
      message: message,
      position: 'bottomRight',
    });
  } else {
    console.warn(message);
  }
}

// region Add a searched product to the quote
//
// The search panel used to offer only "Ver na loja" and a hidden copy-the-link
// on the thumbnail, so getting a product into the quote meant retyping its name
// and price. This fills a price line instead.
//
// Delegated listeners rather than bound ones: the form's innerHTML is replaced
// wholesale on every edit, so anything bound directly would be lost.

let lastFocusedPriceRow = null;

document.addEventListener('focusin', function (event) {
  const input = event.target.closest('.price-fields input');
  if (!input) {
    return;
  }
  lastFocusedPriceRow = {
    section: input.getAttribute('data-section-identifier'),
    service: input.getAttribute('data-service-identifier'),
    price: input.getAttribute('data-price-identifier'),
  };
});

function priceRowFor(target) {
  if (target) {
    const selector =
      '.price-wrapper[data-section-identifier="' +
      target.section +
      '"][data-service-identifier="' +
      target.service +
      '"][data-price-identifier="' +
      target.price +
      '"]';
    const row = document.querySelector(selector);
    if (row) {
      return row;
    }
  }
  // Nothing focused yet, or the row is gone: use the last line in the quote.
  const rows = document.querySelectorAll('.price-wrapper');
  return rows.length ? rows[rows.length - 1] : null;
}

function addProductToQuote(title, cost) {
  const row = priceRowFor(lastFocusedPriceRow);
  if (!row) {
    reportQuoteError('Não há nenhuma linha de preço para preencher.');
    return;
  }
  const description = row.querySelector('[data-form-type="description"]');
  const costField = row.querySelector('[data-form-type="cost"]');
  if (!description || !costField) {
    return;
  }

  description.value = title;
  costField.value = cost;

  const section = row.getAttribute('data-section-identifier');
  const service = row.getAttribute('data-service-identifier');
  const priceId = row.getAttribute('data-price-identifier');
  saveData('description', key, title, section, service, priceId, function () {
    saveData('cost', key, cost, section, service, priceId);
  });

  row.classList.add('price-wrapper-filled');
  setTimeout(() => row.classList.remove('price-wrapper-filled'), 900);
  lastFocusedPriceRow = {
    section: row.getAttribute('data-section-identifier'),
    service: row.getAttribute('data-service-identifier'),
    price: row.getAttribute('data-price-identifier'),
  };
  if (typeof iziToast !== 'undefined') {
    iziToast.success({
      title: 'Adicionado',
      message: title,
      position: 'bottomRight',
      timeout: 2000,
    });
  }
}

document.addEventListener('click', function (event) {
  const button = event.target.closest('.product-add-to-quote');
  if (!button) {
    return;
  }
  event.preventDefault();
  addProductToQuote(button.dataset.title, button.dataset.cost);
});

// endregion

// region Section 2: secondary functions

const saveDataUrl = $('#myForm').attr('data-quote-url');
const filterProductsUrl = $('#myForm').attr('data-product-url');
const deleteFieldUrl = $('#myForm').attr('data-delete-url');
const createFieldUrl = $('#myForm').attr('create-field-url');
const key = $('#myForm').attr('data-key');
let timer;

function saveData(
  action,
  key,
  value,
  section_count,
  service_count,
  price_count,
  onDone,
) {
  $.ajax({
    url: saveDataUrl,
    type: 'GET',
    data: {
      action: action,
      key: key,
      value: value,
      section_count: section_count,
      service_count: service_count,
      price_count: price_count,
      csrfmiddlewaretoken: '{{ csrf_token }}',
    },
    complete: function () {
      if (typeof onDone === 'function') {
        onDone();
      }
    },
  });
}

function deleteField(action, key, section_count, service_count, price_count) {
  $.ajax({
    url: deleteFieldUrl,
    type: 'GET',
    data: {
      action: action,
      key: key,
      section_count: section_count,
      service_count: service_count,
      price_count: price_count,
    },
    success: function (data) {
      // The server answers with form_html even when it refuses the delete, so the
      // form is re-rendered rather than blanked by assigning undefined to it.
      replaceForm(data.form_html);
      reportQuoteError(data.message);
    },
  });
}

function createField(
  action,
  key,
  section_count,
  service_count,
  price_count,
  next_id,
) {
  $.ajax({
    url: createFieldUrl,
    type: 'GET',
    data: {
      action: action,
      key: key,
      section_count: section_count,
      service_count: service_count,
      price_count: price_count,
      next_id: next_id,
    },
    success: function (data) {
      replaceForm(data.form_html);
      reportQuoteError(data.message);
      addChangeSectionEventListeners();
    },
  });
}

function filterProducts(key, value) {
  $.ajax({
    url: filterProductsUrl,
    type: 'GET',
    data: {
      key: key,
      value: value,

      csrfmiddlewaretoken: '{{ csrf_token }}',
    },
    success: function (data) {
      $('#product-results').html(data.form_html);
    },
  });
}

function addChangeSectionEventListeners() {
  let inputSectionElements = document.querySelectorAll('.section-fields input');
  if (inputSectionElements) {
    inputSectionElements.forEach((input) => {
      input.removeEventListener('change', handleSectionChange);
      input.addEventListener('change', handleSectionChange);
    });
  }

  let inputServicesElements = document.querySelectorAll(
    '.service-fields input',
  );
  if (inputServicesElements) {
    inputServicesElements.forEach((input) => {
      input.removeEventListener('change', handleServiceChange);
      input.addEventListener('change', handleServiceChange);
    });
  }

  let inputServices2Elements = document.querySelector(
    '#product-search-form input',
  );
  if (inputServices2Elements) {
    inputServices2Elements.addEventListener(
      'input',
      debounce(handleServiceInputChange, 300),
    );
  }

  let inputPricesElements = document.querySelectorAll('.price-fields input');
  inputPricesElements.forEach((input) => {
    input.removeEventListener('change', handlePriceChange);
    input.addEventListener('change', handlePriceChange);
  });

  let inputNotesElements = document.querySelectorAll('.notes-wrapper input');
  inputNotesElements.forEach((input) => {
    input.removeEventListener('change', handleNotesChange);
    input.addEventListener('change', handleNotesChange);
  });
}

// Define event listener functions
function handleSectionChange(event) {
  let inputValue = event.target.value;
  let inputIdentifier = event.target.getAttribute('data-section-identifier');
  saveData('sections', key, inputValue, inputIdentifier, 0, 0);
}

function handleServiceChange(event) {
  let inputValue = event.target.value;
  let inputSectionIdentifier = event.target.getAttribute(
    'data-section-identifier',
  );
  let inputServiceIdentifier = event.target.getAttribute(
    'data-service-identifier',
  );
  let formType = event.target.getAttribute('data-form-type');
  saveData(
    formType,
    key,
    inputValue,
    inputSectionIdentifier,
    inputServiceIdentifier,
    0,
  );
}

function debounce(func, delay) {
  let timer;
  let debounced = false; // Flag to track if function is already debounced
  return function (...args) {
    if (!debounced) {
      debounced = true;
      clearTimeout(timer);
      timer = setTimeout(() => {
        func.apply(this, args);
        debounced = false; // Reset flag after executing function
      }, delay);
    }
  };
}

function handleServiceInputChange(event) {
  let inputValue = event.target.value;
  filterProducts(key, inputValue);
}

function handlePriceChange(event) {
  let inputValue;
  let checker = 0;
  let inputSectionIdentifier = event.target.getAttribute(
    'data-section-identifier',
  );
  let inputServiceIdentifier = event.target.getAttribute(
    'data-service-identifier',
  );
  let inputPriceIdentifier = event.target.getAttribute('data-price-identifier');
  let formType = event.target.getAttribute('data-form-type');
  if (formType === 'cost' || formType === 'charged') {
    if (isNaN(event.target.value)) {
      checker = 1;
    }
    inputValue = parseFloat(event.target.value.replace(',', '.'));
  } else {
    inputValue = event.target.value;
  }
  if (checker === 0) {
    saveData(
      formType,
      key,
      inputValue,
      inputSectionIdentifier,
      inputServiceIdentifier,
      inputPriceIdentifier,
    );
  }
}

function handleNotesChange(event) {
  let inputValue = event.target.value;
  let formType = event.target.getAttribute('data-form-type');
  saveData(formType, key, inputValue, 0, 0, 0);
}

function confirmDeleteProject(projectKey) {
  let project_Key = projectKey;
  document.getElementById('deleteProjectId').value = project_Key;
  iziToast.question({
    title: 'Confirme',
    message:
      'Tem a certeza de que deseja excluir este projeto? <br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' +
      '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Esta ação será irreversível.',
    position: 'topCenter',
    buttons: [
      [
        '<button>Confirmar</button>',
        function (instance, toast) {
          instance.hide({ transitionOut: 'fadeOut' }, toast, 'button');

          // Submit the form
          document.getElementById(
            'deleteProjectForm',
          ).action = `/builder/projects/delete/${projectKey}/`;
          document.getElementById('deleteProjectForm').submit();
        },
      ],
      [
        '<button>Cancelar</button>',
        function (instance, toast) {
          instance.hide({ transitionOut: 'fadeOut' }, toast, 'button');
        },
      ],
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
    const file_name = file.name;
    const maxLength = 50;
    if (file_name.length > maxLength) {
      label.textContent = file_name.substring(0, maxLength) + '...';
    } else {
      label.textContent = file_name;
    }
  };

  if (file) {
    reader.readAsDataURL(file);
  } else {
    preview.src = '';
  }
}

function previewImageCreate(input) {
  var preview = document.getElementById('imagePreviewCreate');
  var label = document.querySelector('.custom-file-label');
  preview.style.display = 'block';
  var file = input.files[0];
  var reader = new FileReader();

  reader.onloadend = function () {
    preview.src = reader.result;
    const file_name = file.name;
    const maxLength = 50;
    if (file_name.length > maxLength) {
      label.textContent = file_name.substring(0, maxLength) + '...';
    } else {
      label.textContent = file_name;
    }
  };

  if (file) {
    reader.readAsDataURL(file);
  }
}

function previewImageSupplier(input) {
  var preview = document.getElementById('imagePreviewSupplier');
  var label = document.querySelector('.custom-file-label-supplier');
  preview.style.display = 'block';
  var file = input.files[0];
  var reader = new FileReader();

  reader.onloadend = function () {
    preview.src = reader.result;
    const file_name = file.name;
    const maxLength = 50;
    if (file_name.length > maxLength) {
      label.textContent = file_name.substring(0, maxLength) + '...';
    } else {
      label.textContent = file_name;
    }
  };

  if (file) {
    reader.readAsDataURL(file);
  }
}

function previewImageSupplierUpdate(input, supplierId) {
  var preview = document.getElementById('imagePreview' + supplierId);
  var label = document.querySelector('.custom-file-label-update-supplier');
  var file = input.files[0];
  var reader = new FileReader();

  reader.onloadend = function () {
    preview.src = reader.result;
    const file_name = file.name;
    const maxLength = 50;
    if (file_name.length > maxLength) {
      label.textContent = file_name.substring(0, maxLength) + '...';
    } else {
      label.textContent = file_name;
    }
  };

  if (file) {
    reader.readAsDataURL(file);
  } else {
    preview.src = '';
  }
}

function previewImageProductUpdate(input, productId) {
  var preview = document.getElementById('imagePreviewProduct' + productId);
  var label = document.getElementById('product-update-image-label' + productId);
  var file = input.files[0];
  var reader = new FileReader();

  reader.onloadend = function () {
    preview.src = reader.result;
    const file_name = file.name;
    const maxLength = 50;
    if (file_name.length > maxLength) {
      label.textContent = file_name.substring(0, maxLength) + '...';
    } else {
      label.textContent = file_name;
    }
  };

  if (file) {
    reader.readAsDataURL(file);
  } else {
    preview.src = '';
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
          message:
            'Ocorreu um erro ao processar a solicitação. Verifique se a informação está coretamente preenchida.',
        });
      },
    });
  });
});

function scrollFormToBottom() {
  window.scrollBy(0, 10000);
}

document.addEventListener('DOMContentLoaded', function () {
  addChangeSectionEventListeners();
});

// endregion

function submitProjectDownload() {
  document.getElementById('download_project_quote').submit();
}
