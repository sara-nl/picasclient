# .. todo:: import some of the content from the pyproject.toml file
project = 'picasclient'

project_no_spaces = project.replace(' ', '')
version = '1.1.0.dev0'  # import from the toml file
authors = ["Jan Bot, Joris Borgdorff, Lodewijk Nauta, Haili Hu"]       # import from the toml fil

authors_string = ', '.join(authors)
emails = ['servicedesk.surf.nl']
license = 'MIT'  # import from the toml file
copyright = '2025 ' + authors_string
url = 'https://github.com/sara-nl/picasclient'
