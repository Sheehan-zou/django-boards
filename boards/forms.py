from django import forms
from .models import Topic, Post

class NewTopicForm(forms.ModelForm):
    # Widget：用来渲染成HTML元素的工具，如：forms.Textarea对应HTML中的<textarea>标签
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'What is on your mind?'}),
        max_length=4000,
        help_text='The max length of the text is 4000.')

    class Meta:
        model = Topic  # 将Topic表转换成form组件
        fields = ['subject', 'message']  # 指定显示表中的某些字段，由于Topic表中没有message属性，因此前面有forms.CharField

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['message', ]