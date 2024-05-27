import json
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.views.generic import ListView

from .forms import ClientForm
from .models import Client
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template import RequestContext
from ..projects.models import Project
from django.contrib import messages


class ClientListView(LoginRequiredMixin, ListView):
    template_name = 'clients/client_page.html'
    model = Client
    paginate_by = 7
    context_object_name = 'clients'

    def get_queryset(self):
        return Client.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ClientForm(user=self.request.user)
        return context


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
        else:
            contains_letters = any(char.isalpha() for char in updated_nif)
            if contains_letters:
                return JsonResponse({'error': 'O NIF não deve conter letras.'})
        client.name = updated_name
        client.email = updated_email
        client.phone = updated_phone
        client.address = updated_address
        client.nif = updated_nif
        client.save()

        return JsonResponse({'success': 'Informações atualizadas com sucesso'})
    else:
        return JsonResponse({'error': 'Erro ao atualizar o campo. Tente novamente.'})


def delete_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    projects = Project.objects.filter(user=request.user)
    flag = 0
    for project in projects:
        if project.client.id == client.id:
            flag = 1
            break
    if request.method == 'POST' and flag == 0:
        client.delete()
        return redirect('client_list')
    else:
        messages.error(request,
                       "Este cliente tem projetos associados. Apague primeiro os projetos para conseguir apagar o cliente.")
    return redirect('client_list')


def filter_clients(request):
    search_query = request.GET.get('searchClient')
    clients = Client.objects.filter(user=request.user)
    if search_query:
        clients = clients.filter(Q(name__icontains=search_query) | Q(nif__icontains=search_query))
    else:
        clients = Client.objects.filter(user=request.user)[:7]

    return render(request, 'clients/client_page_partial.html', {'clients': clients})
