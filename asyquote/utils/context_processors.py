from asyquote.landingpage.models import FooterTitles, FooterContact, WebsitePages, AdditionalInformation


def titles_context(request):
    titles = FooterTitles.objects.first()
    return {'titles': titles}


def contact_context(request):
    contact = FooterContact.objects.all()
    return {'contact': contact}


def navigation_context(request):
    navigation = WebsitePages.objects.all()
    return {'navigation': navigation}


def additional_context(request):
    additional = AdditionalInformation.objects.all()
    return {'additional': additional}
