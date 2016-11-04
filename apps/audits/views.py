# ~*~ coding: utf-8 ~*~
#
import datetime

from django.views.generic import ListView, UpdateView, DeleteView, DetailView, TemplateView
from django.views.generic.edit import SingleObjectMixin
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.urls import reverse_lazy
from django.conf import settings
from django.db.models import Q

from .models import ProxyLog, CommandLog
from .utils import AdminUserRequiredMixin
from .hands import User, Asset, SystemUser


class ProxyLogListView(AdminUserRequiredMixin, ListView):
    model = ProxyLog
    template_name = 'audits/proxy_log_list.html'
    context_object_name = 'proxy_log_list'

    def get_queryset(self):
        self.queryset = super(ProxyLogListView, self).get_queryset()
        self.keyword = keyword = self.request.GET.get('keyword', '')
        self.username = username = self.request.GET.get('username', '')
        self.ip = ip = self.request.GET.get('ip', '')
        self.date_from_s = date_from_s = \
            self.request.GET.get('date_from', '%s' % (datetime.datetime.now()-datetime.timedelta(7)).strftime('%m/%d/%Y'))
        self.date_to_s = date_to_s = self.request.GET.get('date_to', '%s' % datetime.datetime.now().strftime('%m/%d/%Y'))

        if date_from_s:
            date_from = timezone.datetime.strptime(date_from_s, '%m/%d/%Y')
            self.queryset = self.queryset.filter(date_start__gt=date_from)

        if date_to_s:
            date_to = timezone.datetime.strptime(date_to_s + ' 23:59:59', '%m/%d/%Y %H:%M:%S')
            self.queryset = self.queryset.filter(date_start__lt=date_to)
        if username:
            self.queryset = self.queryset.filter(username=username)
        if ip:
            self.queryset = self.queryset.filter(ip=ip)
        if keyword:
            self.queryset = self.queryset.filter(Q(username__contains=keyword) |
                                                 Q(name__icontains=keyword) |
                                                 Q(hostname__icontains=keyword) |
                                                 Q(ip__icontains=keyword) |
                                                 Q(system_user__icontains=keyword)).distinct()
        return self.queryset

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Audits'),
            'action': _('Proxy log list'),
            'user_list': User.objects.all(),
            'asset_list': Asset.objects.all(),
            'system_user_list': SystemUser.objects.all(),
            'keyword': self.keyword,
            'date_from': self.date_from_s,
            'date_to': self.date_to_s,
        }
        kwargs.update(context)
        return super(ProxyLogListView, self).get_context_data(**kwargs)


class ProxyLogDetailView(AdminUserRequiredMixin, SingleObjectMixin, ListView):
    template_name = 'audits/proxy_log_detail.html'
    context_object_name = 'proxy_log'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=ProxyLog.objects.all())
        return super(ProxyLogDetailView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return list(self.object.commands.all())

    def get_context_data(self, **kwargs):
        context = {
            'app': 'Audits',
            'action': 'Proxy log detail',
        }
        kwargs.update(context)
        return super(ProxyLogDetailView, self).get_context_data(**kwargs)


class ProxyLogCommandsListView(AdminUserRequiredMixin, SingleObjectMixin, ListView):
    template_name = 'audits/proxy_log_commands_list_modal.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=ProxyLog.objects.all())
        return super(ProxyLogCommandsListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return list(self.object.command_log.all())


class CommandLogListView(AdminUserRequiredMixin, ListView):
    model = CommandLog
    template_name = 'audits/command_log_list.html'
    paginate_by = settings.CONFIG.DISPLAY_PER_PAGE
    context_object_name = 'command_list'

    def get_queryset(self):
        # Todo: Default order by lose asset connection num
        self.queryset = super(CommandLogListView, self).get_queryset()
        self.keyword = keyword = self.request.GET.get('keyword', '')
        self.sort = sort = self.request.GET.get('sort', '-datetime')

        if keyword:
            self.queryset = self.queryset.filter()

        if sort:
            self.queryset = self.queryset.order_by(sort)
        return self.queryset

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Audits'),
            'action': _('Command log list'),
            'user_list': User.objects.all(),
            'asset_list': Asset.objects.all(),
            'system_user_list': SystemUser.objects.all(),
        }
        kwargs.update(context)
        return super(CommandLogListView, self).get_context_data(**kwargs)
