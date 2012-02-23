from distutils.core import setup

setup(name = 'slothagent',
      version = '1.0',
      description = 'sloth agent',
      author = ['Lax', 'Ken'],
      author_email = '',
      url = 'https://github.com/xiaonei/sloth',
      packages = ['sloth.agent', 'sloth.agent.modules'],
      package_dir = {
      	'sloth.agent': 'agent',
      	'sloth.agent.modules': 'agent/modules',
      },
      package_data = {
      	'sloth.agent': ['agent/*.py'],
      	'sloth.agent.modules': ['agent/modules/*.py']
      },
     )


setup(name = 'slothserver',
      version = '1.0',
      description = 'sloth server',
      author = ['Lax', 'Ken'],
      author_email = '',
      url = 'https://github.com/xiaonei/sloth',
      packages = ['sloth.server', 'sloth.server.pipes'],
      package_dir = {
      	'sloth.server': 'server',
      	'sloth.server.pipes': 'server/pipes',
      },
      package_data = {
      	'sloth.server': ['server/*.py', 'server/static/*', 'server/templates/*'],
      	'sloth.server.pipes': ['server/pipes/*.py']
      },
     )
