from django import forms

from asyquote.products.models import Products, Category, Supplier


class ProductsForm(forms.ModelForm):
    id = forms.IntegerField(required=False)
    image = forms.ImageField(required=False)
    supplierLink = forms.URLField(required=False)
    supplierPrice = forms.DecimalField(required=False)

    class Meta:
        model = Products
        fields = ['id', 'title', 'suppliers', 'categories', 'image', 'supplierLink', 'supplierPrice']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['placeholder'] = 'Insira o título do produto...'
        self.fields['suppliers'].widget.attrs['placeholder'] = 'Insira os fornecdores do produto...'
        self.fields['categories'].widget.attrs['placeholder'] = 'Insira as categorias do produto...'


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name_category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name_category'].widget.attrs['placeholder'] = 'Insira o nome da categoria...'


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name_supplier', 'image_supplier']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name_supplier'].widget.attrs['placeholder'] = 'Insira o nome do fornecedor...'
        self.fields['image_supplier'].widget.attrs['placeholder'] = 'Insira a imagem do fornecedor...'


class UploadExcelForm(forms.Form):
    excel_file = forms.FileField(label='Upload Excel File')
