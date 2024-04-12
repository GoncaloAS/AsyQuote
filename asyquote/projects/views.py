import json
from django.db.models import Max
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProjectForm
from .models import Project, SectionQuote, ServicesQuote, PricesQuote, Notes
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
import openpyxl
from openpyxl.styles import PatternFill, Font
from openpyxl.utils import get_column_letter
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from wagtail.blocks import StreamValue
from ..clients.models import Client


@login_required
def project_list(request):
    state = "EM ESPERA"
    projects = Project.objects.filter(user=request.user, state=state)
    form = ProjectForm(user=request.user)
    form.fields['client'].queryset = form.fields['client'].queryset.order_by('name')
    return render(request, 'builder/builder_projects.html', {'projects': projects, 'form': form})


def edit_project(request, key):
    project = get_object_or_404(Project, key=key)
    if project.user != request.user:
        return render(request, 'builder/project_not_found.html')
    clients = Client.objects.all()
    sections = SectionQuote.objects.filter(project_key=key)
    services = ServicesQuote.objects.filter(project_key=key)
    prices = PricesQuote.objects.filter(project_key=key)
    notes = Notes.objects.filter(project_key=key)

    return render(request, 'builder/edit_project.html',
                  {'project': project, 'clients': clients, 'sections': sections, 'services': services, 'prices': prices,
                   'notes': notes})


def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            last_project = Project.objects.order_by('-id').first()
            if last_project:
                last_project_id = last_project.id
            else:
                last_project_id = 0

            new_id = last_project_id + 1
            form.cleaned_data['id'] = new_id

            project = form.save(commit=False)
            project.user = request.user  # Set the user
            project.state = 'EM ESPERA'
            uploaded_image = request.FILES.get('image')
            if uploaded_image:
                project.image = uploaded_image
            project.save()

            messages.success(request, 'Projeto criado com sucesso!')
            return redirect('project_list')
        else:
            print(form.errors)
            messages.error(request, 'Erro ao criar projeto. Verifique se as informações estão corretas.')
            return redirect('project_list')
    else:
        form = ProjectForm()

    return render(request, 'builder/builder_projects.html', {'form': form})


def filter_projects(request):
    state = request.GET.get('state', None)
    projects = Project.objects.filter(user=request.user)

    if state:
        projects = projects.filter(state=state, user=request.user)

    html = render_to_string('builder/project_list_partial.html', {'projects': projects})
    return HttpResponse(html)


def filter_projects_data(request):
    state = request.GET.get('state', None)
    projects = Project.objects.filter(user=request.user)

    if state:
        projects = projects.filter(state=state, user=request.user)
    html = render_to_string('builder/project_list_data_partial.html',
                            {'projects': projects})
    return HttpResponse(html)


def list_projects_table(request):
    state = "EM EXECUÇÃO"
    projects = Project.objects.filter(user=request.user, state=state)
    return render(request, 'builder/project_list.html', {'projects': projects})


def download_excel(request):
    state = request.GET.get('state')
    if state == None:
        state = "EM EXECUÇÃO"
        projects = Project.objects.filter(state=state, user=request.user).order_by('quote_number')
    elif state:
        projects = Project.objects.filter(state=state, user=request.user).order_by('quote_number')
    else:
        projects = Project.objects.filter(user=request.user).order_by('quote_number')
    if not projects:
        messages.info(request, "Não foi encontrado nehum projeto com estas condições")
        return redirect('list_projects_table')
    wb = openpyxl.Workbook()
    ws = wb.active

    # Add heading row
    heading_row = ['Ref. Orçamento', 'Título', 'Cliente', 'Localização', 'Valor', 'Estado']
    ws.append(heading_row)

    for cell in ws[1]:
        cell.fill = PatternFill(start_color='808080', end_color='808080', fill_type='solid')
        cell.font = Font(color='FFFFFF', bold=True)

    # Add data rows
    for project in projects:
        ws.append([project.quote_number, project.title, project.client.name, project.address,
                   project.value, project.state])

    total_value = sum(project.value for project in projects)
    total_row = ['Total', '', '', '', '', '', total_value]
    ws.append(total_row)
    total_cell = ws.cell(row=len(projects) + 2, column=1)
    total_cell.fill = PatternFill(start_color='05af50', end_color='05af50', fill_type='solid')
    total_cell.font = Font(color='FFFFFF', bold=True)

    for col in range(1, len(heading_row) + 1):
        max_length = 0
        for row in range(1, len(projects) + 3):
            cell_value = ws.cell(row=row, column=col).value
            if cell_value is not None:
                cell_length = len(str(cell_value))
                if cell_length > max_length:
                    max_length = cell_length
        adjusted_width = max_length + 2
        ws.column_dimensions[get_column_letter(col)].width = adjusted_width

    # Save the response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    if state:
        filename = f"projetos_{state.lower().replace(' ', '_')}.xlsx"
    else:
        filename = "projetos.xlsx"

    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response


def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        project.delete()
        return redirect('project_list')
    return render(request, 'builder/delete_project.html', {'project': project})


def update_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':

        updated_title = request.POST.get('update_title')
        updated_address = request.POST.get('update_address')
        updated_state = request.POST.get('update_state')
        updated_client_id = request.POST.get('update_project_client')
        uploaded_image = request.FILES.get('update_image')
        if uploaded_image:
            project.image = uploaded_image
        if updated_title and updated_address:
            project.title = updated_title
            project.address = updated_address
            updated_client = get_object_or_404(Client, pk=updated_client_id)
            project.state = updated_state
            project.client = updated_client
            project.save()
            return JsonResponse({'success': 'Informações atualizadas com sucesso'})
    else:
        return JsonResponse({'error': 'Informação errada'})


def save_quote_url(request):
    if request.method == 'GET':
        action = request.GET.get('action')
        key = request.GET.get('key')
        if action == 'add-section':
            # section_creation
            max_section_count = SectionQuote.objects.filter(project_key=key).aggregate(Max('section_count'))
            next_section_count = max_section_count['section_count__max'] + 1 if max_section_count[
                                                                                    'section_count__max'] is not None else 1
            SectionQuote.objects.create(project_key=key, section_count=next_section_count)

            # services_creation
            ServicesQuote.objects.create(project_key=key, service_count=1, section_key=next_section_count)

            # prices_creation
            PricesQuote.objects.create(project_key=key, prices_count=1, services_key=1)

        if action == 'add-service':
            # get the latest section count
            max_section_count = SectionQuote.objects.filter(project_key=key).aggregate(Max('section_count'))
            next_section_count = max_section_count['section_count__max']

            # get the latest service count for the current section
            max_services_count = ServicesQuote.objects.filter(project_key=key,
                                                              section_key=next_section_count).aggregate(
                Max('service_count'))
            next_service_count = max_services_count['service_count__max'] + 1 if max_services_count[
                                                                                     'service_count__max'] is not None else 1

            # services_creation
            ServicesQuote.objects.create(project_key=key, service_count=next_service_count,
                                         section_key=next_section_count)

            # get the latest price count for the current service
            max_prices_count = PricesQuote.objects.filter(project_key=key, services_key=next_service_count).aggregate(
                Max('prices_count'))
            next_prices_count = max_prices_count['prices_count__max'] + 1 if max_prices_count[
                                                                                 'prices_count__max'] is not None else 1

            # prices_creation
            PricesQuote.objects.create(project_key=key, prices_count=next_prices_count, services_key=next_service_count)

        if action == 'add-price':
            # get the latest section count
            max_section_count = SectionQuote.objects.filter(project_key=key).aggregate(Max('section_count'))
            next_section_count = max_section_count['section_count__max']

            # get the latest service count for the current section
            max_services_count = ServicesQuote.objects.filter(project_key=key,
                                                              section_key=next_section_count).aggregate(
                Max('service_count'))
            next_service_count = max_services_count['service_count__max']

            # get the latest price count for the current service
            max_prices_count = PricesQuote.objects.filter(project_key=key, services_key=next_service_count).aggregate(
                Max('prices_count'))
            next_prices_count = max_prices_count['prices_count__max'] + 1 if max_prices_count[
                                                                                 'prices_count__max'] is not None else 1

            # prices_creation
            PricesQuote.objects.create(project_key=key, prices_count=next_prices_count, services_key=next_service_count)

        return redirect(request.META.get('HTTP_REFERER', '/'))
