#!/usr/bin/env python
# coding: utf-8
#
# xiaoyu <xiaokong1937@gmai.com>
#
# 2014/02/11
#
# Mixins for xx project
#
import json

from django.http import HttpResponse


class JSONResponseMixin(object):
    """JSON mixin"""
    def render_to_response(self, context):
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        return HttpResponse(content,
                            content_type='application/json',
                            **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        return json.dumps(context)
