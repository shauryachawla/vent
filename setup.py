from setuptools import setup, find_packages

setup(
    name='vent',
    version='0.3.0',
    packages=['vent', 'vent.core', 'vent.core.file-drop', 'vent.core.rq-worker',
              'vent.core.rq-dashboard', 'vent.core.template-change',
              'vent.core.rmq-es-connector', 'vent.helpers'],
    data_files=[('vent/scripts', ['scripts/bootlocal.sh', 'scripts/bootsync.sh',
                                  'scripts/build.sh', 'scripts/build_images.sh',
                                  'scripts/build_local.sh', 'scripts/custom',
                                  'scripts/wrapper.sh']),
                ('vent/scripts/info_tools', ['scripts/info_tools/get_info.sh',
                                             'scripts/info_tools/get_logs.py',
                                             'scripts/info_tools/get_messages.sh',
                                             'scripts/info_tools/get_namespaces.py',
                                             'scripts/info_tools/get_services.sh',
                                             'scripts/info_tools/get_stats.sh',
                                             'scripts/info_tools/get_status.py',
                                             'scripts/info_tools/get_tasks.sh',
                                             'scripts/info_tools/get_tools.sh',
                                             'scripts/info_tools/get_types.sh',
                                             'scripts/info_tools/get_visualization.sh']),
                ('vent/scripts/service_urls', ['scripts/service_urls/get_elasticsearch_head_url.sh',
                                               'scripts/service_urls/get_elasticsearch_marvel_url.sh',
                                               'scripts/service_urls/get_rabbitmq_url.sh',
                                               'scripts/service_urls/get_rqdashboard_url.sh',
                                               'scripts/service_urls/get_urls.py']),
                ('vent', ['vent/help']),
                ('vent/templates', ['vent/templates/core.template',
                                    'vent/templates/modes.template'])],
    scripts=['scripts/vent-cli', 'scripts/vent', 'scripts/vent-generic'],
    license='Apache License 2.0',
    author='arpit',
    author_email='',
    maintainer='Charlie Lewis',
    maintainer_email='clewis@iqt.org',
    description='A self-contained virtual appliance based on boot2docker that provides a platform to collect and analyze data across a flexible set of tools and technologies.',
    keywords='docker containers platform collection analysis tools devops',
    url='https://github.com/CyberReboot/vent',
)
