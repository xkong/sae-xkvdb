#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/03/03
#
# GenericViews for xkvdb app
# 
# Kvdb manager
#
import csv
from StringIO import StringIO

from django.views.generic.base import TemplateView, View
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.http import StreamingHttpResponse

import sae.kvdb
import xlwt

from .mixin import JSONResponseMixin


def superuser_required(function=None,
                       redirect_field_name=REDIRECT_FIELD_NAME,
                       login_url=None):
    """
    Decorator for views that checks that the user is superuser, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_superuser,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


class Echo(object):
    def write(self, value):
        return value


class KVDBIndexView(TemplateView):
    template_name = 'xkvdb/index.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        self.client = sae.kvdb.KVClient()
        summary = self.client.get_info()
        context.update({'summary': summary})
        return self.render_to_response(context)

    @method_decorator(superuser_required)
    def dispatch(self, *args, **kwargs):
        return super(KVDBIndexView, self).dispatch(*args, **kwargs)


class KVDBView(JSONResponseMixin, View):
    '''
    JSON backend for KVDB request.
    '''
    def post(self, request, *args, **kwargs):
        self.client = sae.kvdb.KVClient()
        action = request.POST.get('action', 'get_by_prefix')
        code = 0
        if action == 'get_by_prefix':
            prefix = request.POST.get('prefix')
            prefix = prefix.encode('utf-8')
            limit = request.POST.get('limit')
            limit = limit or 10
            marker = request.POST.get('marker', None)
            data = []
            items = [i for i in self.client.get_by_prefix(prefix,
                                                          limit=int(limit),
                                                          marker=marker)]
            for k, v in items:
                data.append({'key': k, 'value': v})
        elif action == 'del':
            key = request.POST.get('key')
            key_hash = key.encode('utf-8')
            if not key:
                data = False
            else:
                data = self.client.delete(key_hash)
        elif action == 'update':
            key = request.POST.get('key')
            value = request.POST.get('value')
            value = self._clean_value(value)
            key_hash = key.encode('utf-8')
            if not key:
                data = False
            else:
                data = self.client.set(key_hash, value)
        elif action == 'add':
            key = request.POST.get('key')
            value = request.POST.get('value')
            value = self._clean_value(value)
            key_hash = key.encode('utf-8')
            if not key:
                data = 'Invalid key'
                code = -1
            else:
                pre_value = self.client.get(key_hash)
                if pre_value != value:
                    self.client.add(key_hash, value)
                    data = []
                    data.append({'key': key, 'value': value})
                else:
                    data = ''
        return self.render_to_response({'code': code, 'msg': data})

    @method_decorator(superuser_required)
    def dispatch(self, *args, **kwargs):
        return super(KVDBView, self).dispatch(*args, **kwargs)

    def _clean_value(self, value):
        '''
        Clean value for key.
        Currently we just replace `<br>` with ``.
        '''
        result = value.replace('<br>', '')
        if result.find(',') != -1:
            result = result.split(',')
        return result


class KVDBExportView(JSONResponseMixin, View):
    '''
    KVDB data export view.
    Used for backup KVDB data.
    '''
    @method_decorator(superuser_required)
    def dispatch(self, *args, **kwargs):
        return super(KVDBExportView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.client = sae.kvdb.KVClient()
        format_ = request.POST.get('format', 'json')

        if format_ == 'json':
            return self._export_json(request)
        elif format_ == 'csv':
            return self._export_csv(request)
        elif format_ == 'excel':
            return self._export_xls(request)

    def _export_json(self, request, ext='json'):

        prefix, limit, filename = self._pre_export(request, ext=ext)
        ret = {}
        for k, v in self.client.get_by_prefix(prefix, limit=int(limit)):
            ret[k] = v
        response = self.render_to_response(ret)
        response['Content-Disposition'] = 'attachment; filename="%s"' % \
                                           filename
        return response

    def _export_csv(self, request, ext='csv'):

        prefix, limit, filename = self._pre_export(request, ext=ext)

        buffer_ = Echo()
        writer = csv.writer(buffer_)
        response = StreamingHttpResponse((writer.writerow(row) for row in \
                self.client.get_by_prefix(prefix, limit=int(limit))),
                                         content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' %\
                                          filename
        return response

    def _export_xls(self, request, ext='xls'): 
        prefix, limit, filename = self._pre_export(request, ext=ext)
        
        # Zero-indexed  
        MAX_ROW = 65532

        def stream():
            wb = xlwt.Workbook(encoding='utf-8')
            ws_list = []
            temp_file = StringIO()
            for j in range(int(limit) / MAX_ROW + 1):
                ws_list.append(wb.add_sheet('%s_%s' % (prefix or 'all', j)))
            sheet_index = index_ = 0;
            for item in self.client.get_by_prefix(prefix, limit=int(limit)):
                if index_ >  (sheet_index + 1) * MAX_ROW:
                    sheet_index += 1
                ws = ws_list[sheet_index]
                ws.write(index_ - sheet_index * MAX_ROW, 0, item[0])
                if isinstance(item[1], list):
                    value = ','.join(v for v in item[1])
                else:
                    value = item[1]
                ws.write(index_ - sheet_index * MAX_ROW, 1, value)
                index_ += 1
            wb.save(temp_file)
            return temp_file.getvalue()

        content_type = 'application/vnd.ms-excel; charset=utf-16'
        response = StreamingHttpResponse(stream(),
                                         content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename="%s"' %\
                                          filename
        return response

    def _pre_export(self, request, ext='csv'):
        prefix = request.POST.get('prefix').encode('utf-8')
        limit = request.POST.get('limit')
        limit = limit or 100
        name_ = prefix or 'all'
        filename = '%s.%s' % (name_, ext)
        return prefix, limit, filename
