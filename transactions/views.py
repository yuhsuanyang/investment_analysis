from django.shortcuts import render


# Create your views here.
def main(request):
    data = {'message': 'hi'}
    return render(request, 'index.html', context=data)
