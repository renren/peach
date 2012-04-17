from distutils.core import setup


setup(name = 'peach',
      version = '1.0',
      description = 'The realtime monitor, agent module',
      author = 'Lax & Ken',
      author_email = '',
      url = 'https://github.com/xiaonei/peach',
      packages = ['peach', 'peach.agent', 'peach.agent.modules', 'peach.server', 'peach.server.pipes'],
      package_dir = {
                'peach': '.',
                'peach.agent': 'agent',
                'peach.agent.modules': 'agent/modules',
                'peach.server': 'server',
                'peach.server.pipes': 'server/pipes',
      },
      package_data = {
        'peach': ['__init__.py'],
      	'peach.agent': ['agent/*.py'],
      	'peach.agent.modules': ['agent/modules/*.py'],
      },
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
      scripts = ['peach-agent']
     )
