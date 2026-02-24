from django.contrib.auth.models import Group
from django.forms import ModelForm, Form, FileField

from .models import Product

class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ["name"]


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ("name", "description", "price", "discount", "archived", "preview")


class CSVImportForm(Form):
    csv_file = FileField()