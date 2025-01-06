from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from .models import Package, Tag

def validate_image_size(value):
    filesize = value.size
    max_size = 2 * 1048576
    
    if filesize > max_size:
        raise ValidationError(f'Maximum file size is 2MB. Current file size is {filesize/1048576}')

class MultipleFileInput(forms.FileInput):
    def __init__(self, attrs=None):
        super().__init__(attrs)
        if not attrs:
            attrs = {}
        attrs['multiple'] = 'multiple'
        self.attrs = attrs

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        return files.get(name, None)

class PackageSubmissionForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter tags separated by commas'}),
        help_text="Separate tags with commas",
        validators=[MaxLengthValidator(60)]  
    )

    title = forms.CharField(
        max_length=25,  
        widget=forms.TextInput(attrs={'placeholder': 'Enter title'}),
    )

    description = forms.CharField(
        max_length=120,  
        widget=forms.Textarea(attrs={'placeholder': 'Enter description'}),
    )

    
    thumbnail = forms.ImageField(
        validators=[validate_image_size],
        required=False  
    )

    class Meta:
        model = Package
        fields = ['title', 'description', 'tags', 'thumbnail', 'external_link']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['tags'] = ', '.join(self.instance.tags.values_list('name', flat=True))

    def clean_tags(self):
        tags_input = self.cleaned_data.get('tags', '')
        if tags_input:
            tag_names = [tag.strip() for tag in tags_input.split(',') if tag.strip()] # split tags by ,
            return tag_names
        return []

    def save(self, commit=True):
        package = super().save(commit=False)
        if commit:
            package.save()

        # Remove tags and add new ones
        tag_names = self.cleaned_data.get('tags')
        if tag_names:
            package.tags.clear()
            for tag_name in tag_names:
                tag = Tag.objects.get_or_create(name=tag_name)
                package.tags.add(tag)
        
        return package