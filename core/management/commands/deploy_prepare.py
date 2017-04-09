from django.core.management import BaseCommand
from django.template.loader import render_to_string
import subprocess
import shlex
from application.settings.base import BASE_DIR


class Command(BaseCommand):
    help = 'Rendering deploy templates'

    def handle(self, *args, **options):

        context = {
            'project_name': 'letsgo',
            'project_version': '1.0-7'
        }

        postinst_tpl = 'debian/postinst.tpl'
        control_tpl = 'debian/control.tpl'

        content = render_to_string(postinst_tpl, context)

        with open(BASE_DIR + '/../deploy_tools/main/DEBIAN/postinst', 'w') as f:
            f.write(content)

        content = render_to_string(control_tpl, context)

        with open(BASE_DIR + '/../deploy_tools/main/DEBIAN/control', 'w') as f:
            f.write(content)

        self.stdout.write('Rendering successfully completed')
