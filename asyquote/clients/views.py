import json
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .forms import ClientForm
from .models import Client
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext



@login_required
def client_list(request):
    clients = Client.objects.filter(user=request.user)
    form = ClientForm(user=request.user)
    return render(request, 'clients/client_page.html', {'clients': clients, 'form': form})


def create_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            nif = form.cleaned_data['nif']
            if len(nif) != 9:
                return JsonResponse({'error': 'O NIF deve ter exatamente 9 dígitos.'})
            if Client.objects.filter(nif=nif, user=request.user).exists():
                # Client already exists, show iziToast error notification
                return JsonResponse({'error': 'Erro ao adicionar cliente. Este cliente já existe.'})
            last_client = Client.objects.order_by('-id').first()
            if last_client:
                last_client_id = last_client.id
            else:
                last_client_id = 0

            new_id = last_client_id + 1
            form.cleaned_data['id'] = new_id

            client = form.save(commit=False)
            client.user = request.user
            client.save()
            return JsonResponse({'success': 'Cliente adicionado com sucesso'})
        else:
            errors = json.loads(form.errors.as_json())
            return JsonResponse({'error': errors})
    else:
        form = ClientForm()

    return render(request, 'clients/client_page.html', {'form': form})


def update_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    if request.method == 'POST':

        updated_name = request.POST.get('update_name')
        updated_email = request.POST.get('update_email')
        updated_phone = request.POST.get('update_phone')
        updated_address = request.POST.get('update_address')
        updated_nif = request.POST.get('update_nif')

        if len(updated_nif) != 9:
            return JsonResponse({'error': 'O NIF deve ter exatamente 9 dígitos.'})
        client.name = updated_name
        client.email = updated_email
        client.phone = updated_phone
        client.address = updated_address
        client.nif = updated_nif
        client.save()

        return JsonResponse({'success': 'Informações atualizadas com sucesso'})
    else:
        return JsonResponse({'error': 'Informação errada'})


def delete_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    if request.method == 'POST':
        client.delete()
        return redirect('client_list')
    clients = Client.objects.filter(user=request.user)
    return render(request, 'clients/client_page.html', {'clients': clients})


def filter_clients(request):
    search_query = request.GET.get('searchClient')
    clients = Client.objects.filter(user=request.user)
    if search_query:
        clients = clients.filter(Q(name__icontains=search_query) | Q(nif__icontains=search_query))
    return render(request, 'clients/client_page_partial.html', {'clients': clients})


