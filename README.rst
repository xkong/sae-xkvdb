=====
SAE-kvdb
=====

SAE-kvdb is a simple Django app to conduct management of SAE-kvdb. With this
tool you can add, delete, update data for kvdb, or export data from kvdb as
json, excel, csv format.

Hope this tool can help you.

For bug report or feedback, please contact xiaokong1937#gmail.com

Quick start
-----------

1. Add "xkvdb" to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'xkvdb',
      )

2. Include the xkvdb URLconf in your project urls.py like this::

      url(r'^xkvdb/', include('xkvdb.urls')),

3. Run `python manage.py syncdb` to create the xkvdb models.(Unnecessary for
   now.)

4. Start the development server and visit http://127.0.0.1:8000/xkvdb/ for 
   local SAE kvdb management.(You should has SAE local-environment work and
   specify the kvdb file with command-line args by using
   `--kvdb-file=/path/to/your/kvdb.file/`)

5. Visit http://127.0.0.1:8000/xkvdb/ to participate in the SAE-kvdb.
