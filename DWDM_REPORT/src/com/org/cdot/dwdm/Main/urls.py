"""dJangoApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include,url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from . import main
from . import view
from django.views.generic import TemplateView
urlpatterns = [
    url(r'^dataFileRead/$',TemplateView.as_view(template_name="Main/data.json", content_type="json"), name="data_file"),
    url(r'^logFileRead/$',TemplateView.as_view(template_name="Main/log.json", content_type="json"), name="log_file"),
    url(r'^getGneInfo/$',main.Definitions.get_gne_info),
    url(r'^runMainHandler/$',main.main),
    url(r'^ipMapping/$',main.Definitions.get_ip2_to_ip1_mapping),
    url(r'^runGetSetHandler/$',main.Definitions.get_set_main_function),
    url(r'^runTrapHandler/$',main.snmpApi.receive_trap),
    url(r'^$',view.formAction),
    url(r'^Main/$',view.formAction),
    url(r'^admin/', admin.site.urls),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
