from distutils.core import setup

author = 'Lax & Ken'
email = ''
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

setup(name = 'peachagent',
      version = '1.0',
      description = 'The realtime monitor, agent module',
      author = author,
      author_email = email,
      url = 'https://github.com/xiaonei/peach',
      packages = ['peach.agent', 'peach.agent.modules'],
      package_dir = {
      	'peach.agent': 'agent',
      	'peach.agent.modules': 'agent/modules',
      },
      package_data = {
      	'peach.agent': ['agent/*.py'],
      	'peach.agent.modules': ['agent/modules/*.py']
      },
      classifiers = classifiers,
      scripts = ['peach-agent']
     )


setup(name = 'peachserver',
      version = '1.0',
      description = 'The realtime monitor, server module',
      author = author,
      author_email = email,
      url = 'https://github.com/xiaonei/peach',
      packages = ['peach.server', 'peach.server.pipes'],
      package_dir = {
      	'peach.server': 'server',
      	'peach.server.pipes': 'server/pipes',
      },
      package_data = {
      	'peach.server': ['server/*.py', 'server/static/*', 'server/templates/*'],
      	'peach.server.pipes': ['server/pipes/*.py']
      },
      classifiers = classifiers
     )
