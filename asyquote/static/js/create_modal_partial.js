document.addEventListener('DOMContentLoaded', function () {
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
                            <div class="col-12 col-md-6">
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
});
