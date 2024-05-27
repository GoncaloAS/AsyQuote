document.addEventListener('DOMContentLoaded', function () {
    var suppliersSelect = document.getElementById('id_suppliers');
    var supplierLinkFields = document.getElementById('supplierLinkFields');
    let previousSwitchState = false;
    suppliersSelect.addEventListener('change', function () {
        // Clear existing supplier link fields
        supplierLinkFields.innerHTML = '';

        // Get selected suppliers
        var selectedSuppliers = suppliersSelect.selectedOptions;

        // Show input fields for each selected supplier
        for (var i = 0; i < selectedSuppliers.length; i++) {
            var supplierId = selectedSuppliers[i].value;
            var supplierName = selectedSuppliers[i].text;

            var inputField = document.createElement('div');
            inputField.classList.add('form-group');
            inputField.innerHTML = `
                <label class="label_form_create_project" for="id_supplierLink_${supplierId}">Link do Fornecedor (${supplierName}):</label>
                <input type="text" id="id_supplierLink_${supplierId}" name="supplierLink_${supplierId}" class="form-control" required>
                <label class="label_form_create_project" for="id_supplierPrice_${supplierId}">Preço do Fornecedor (${supplierName}):</label>
                <input type="number" id="id_supplierPrice_${supplierId}" name="supplierPrice_${supplierId}" class="form-control" required min="0" step="any">
            `;
            supplierLinkFields.appendChild(inputField);
        }

        // Show the field container if there are selected suppliers
        if (selectedSuppliers.length > 0) {
            supplierLinkFields.style.display = 'block';
        } else {
            supplierLinkFields.style.display = 'none';
        }
    });
});

function attachProductModalListeners() {
    const productModals = document.querySelectorAll('[data-bs-toggle="modal"]');
    productModals.forEach(function (productModal) {
        productModal.addEventListener('click', function () {
            const productId = productModal.getAttribute('data-product-id');
            const productTitle = productModal.getAttribute('data-product-title');
            const productImage = productModal.getAttribute('data-product-image');
            const supplierImages = productModal.getAttribute('data-supplier-image');
            const productPrices = productModal.getAttribute('data-product-price');
            const productLinksUrl = productModal.getAttribute('data-product-links-url');

            if (productId && productTitle && productImage && supplierImages && productPrices && productLinksUrl) {
                const supplierImagesArray = supplierImages.split(/\s+/);
                const productPricesArray = productPrices.split(/\s+/);
                const productLinksUrlArray = productLinksUrl.split(/\s+/);

                const modalBody = document.querySelector('#staticProductInfo .modal-body');

                let suppliersHTML = '';
                for (let i = 0; i < supplierImagesArray.length; i++) {
                    if (supplierImagesArray[i] !== '') {
                        suppliersHTML += `
                            <div class="stores-info-product mt-4">
                                <div class="d-flex align-items-center mb-2 justify-content-between px-3">
                                    <div class="mr-3">
                                        <img src="${supplierImagesArray[i]}" alt="Supplier Image" class="supplier-image" style="width: 60px;">
                                    </div>
                                    <div class="mr-3">
                                        <p class="font_family_products color_price_products">${productPricesArray[i]}&nbsp;EUR</p>
                                    </div>
                                    <div class="supplier-info">
                                        <button class="supplier-link">
                                            <a href="${productLinksUrlArray[i]}" target="_blank">Ver na Loja</a>
                                        </button>
                                    </div>
                                </div>
                            </div>`;
                    }
                }

                modalBody.innerHTML = `
                    <div class="container">
                        <div class="row product-info-modal">
                            <div class="col-12 col-md-6 product-image-info-div">
                                <img src="${productImage}" alt="${productTitle}" class="product-image-info">
                            </div>
                            <div class="col-12 col-md-6">
                                <h3 class="text-uppercase">${productTitle}</h3>
                                ${suppliersHTML}
                            </div>
                        </div>
                    </div>`;
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', attachProductModalListeners);

document.body.addEventListener('htmx:afterSwap', attachProductModalListeners);


function updateEditor() {
    let switchElement = document.getElementById("switch");
    let addProduct = document.getElementById("product_add_more");
    let uploadFile = document.getElementById("product_excel_upload");
    let filteredProducts = document.getElementsByClassName("filtered_products");
    let updateSupplierDropdown = document.getElementById("updateSupplierDropdown");
    let createSupplierDropdown = document.getElementById("createSupplierDropdown");
    let updateCategoryDropdown = document.getElementById("updateCategoryDropdown");
    let createCategoryDropdown = document.getElementById("createCategoryDropdown");
    const productCards = document.querySelectorAll('.filtered_products');

    if (switchElement) {
        if (switchElement.checked) {
            addProduct.style.display = 'none';
            uploadFile.style.display = 'flex';
            updateSupplierDropdown.style.display = 'block';
            createSupplierDropdown.style.display = 'none';
            createCategoryDropdown.style.display = 'none';
            updateCategoryDropdown.style.display = 'block';
            Array.from(filteredProducts).forEach(container => {

                let links = container.querySelectorAll("a[data-bs-toggle='modal'][data-bs-target='#staticProductInfo']");
                links.forEach(link => {
                    productCards.forEach(card => {
                        const productId = link.getAttribute('data-product-id');
                        const modalId = `#staticProductUpdate${productId}`;
                        link.dataset.bsTarget = modalId;
                        link.setAttribute('data-bs-target', modalId);
                    });
                });
            })


        }
        if (!(switchElement.checked)) {
            addProduct.style.display = 'flex';
            uploadFile.style.display = 'none';
            updateSupplierDropdown.style.display = 'none';
            createSupplierDropdown.style.display = 'block';
            createCategoryDropdown.style.display = 'block';
            updateCategoryDropdown.style.display = 'none';
            Array.from(filteredProducts).forEach(container => {
                let links = container.querySelectorAll("a[data-bs-toggle='modal'][data-bs-target^='#staticProductUpdate']");
                links.forEach(link => {
                    const productId = link.getAttribute('data-product-id');
                    const modalId = `#staticProductInfo`;
                    link.dataset.bsTarget = modalId;
                    link.setAttribute('data-bs-target', modalId);
                });
            });
        }

    }

    document.removeEventListener("htmx:afterSwap", afterSwapHandler);
}


function afterSwapHandler(evt) {
    if (evt.target.id === 'search-results') {
        setTimeout(updateEditor, 100);

    }
}

var afterSwapHandler = afterSwapHandler.bind(this);
document.addEventListener("htmx:afterSwap", afterSwapHandler);


document.addEventListener("DOMContentLoaded", function () {
    const productCards = document.querySelectorAll('.filtered_products');
    productCards.forEach(function (card) {
        card.addEventListener('click', function (e) {
            e.preventDefault();
            const productId = card.getAttribute('data-product-id');
            const modalId = `#staticProductUpdate${productId}`;
            const modal = new bootstrap.Modal(document.querySelector(modalId));
            modal.show();
        });
    });
});


function handleSuppliersChange(productId) {
    console.log(productId);
    const supplierLinkFields = document.getElementById("supplierLinkFields" + productId);
    const linksFormGroup = document.getElementById("linksFormGroup" + productId)
    supplierLinkFields.style.display = 'block';
    linksFormGroup.innerHTML = '';
    linksFormGroup.style.display = 'none';
    supplierLinkFields.innerHTML = '';

    let selectedOptions = document.querySelectorAll('#id_suppliers' + productId + ' option:checked');
    selectedOptions.forEach(function (option) {
        let supplierId = option.value;
        let supplierName = option.text;
        let supplierLink = document.querySelector('#id_supplierLink_' + supplierId);


        let inputField = document.createElement('div');
        inputField.classList.add('form-group');
        inputField.innerHTML = `
                <label class="label_form_create_project" for="id_supplierLink_${supplierId}">Link do Fornecedor (${supplierName}):</label>
                <input type="text" id="id_supplierLink_${supplierId}" name="supplierLink_${supplierId}" class="form-control" required>
                <label class="label_form_create_project" for="id_supplierPrice_${supplierId}">Preço do Fornecedor (${supplierName}):</label>
                <input type="number" id="id_supplierPrice_${supplierId}" name="supplierPrice_${supplierId}" class="form-control" required min="0" step="any">
            `;
        supplierLinkFields.appendChild(inputField);
    });
}

function HideFormExcel(){
    form_excel = document.getElementById("staticExcelUpload");
    form_excel.style.display = "none";
    excel_preloader = document.getElementById("excel_preloader_img")
    excel_preloader.style.display = "block"
    excel_preloader.style.zIndex = "1000";
}
