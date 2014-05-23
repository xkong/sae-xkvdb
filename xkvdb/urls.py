#!/usr/bin/env python
# coding: utf-8

from django.conf.urls import patterns, url

from .genericviews import (KVDBIndexView, KVDBView,
                           KVDBExportView)

urlpatterns = patterns(
    '',
    url(r'^$', KVDBIndexView.as_view(), name="kvdb_index"),
    url(r'^do/$', KVDBView.as_view(), name="kvdb_do"),
    url(r'^export/$', KVDBExportView.as_view(), name="kvdb_export"),
)
