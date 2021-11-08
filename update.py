import json
import os
import requests
import shutil
from bs4 import BeautifulSoup, Comment
from glob import glob
from io import BytesIO
from packaging.utils import parse_wheel_filename, parse_sdist_filename
from zipfile import ZipFile

packages = {
    'argparse',
    'anyio',
    'appdirs',
    'atomicwrites',
    'attrs',
    'awscli',
    'awslambdaric',
    'aws-sam-translator',
    'aws-xray-sdk',
    'backcall',
    'boto',
    'boto3',
    'botocore',
    'cachecontrol',
    'certifi',
    'cffi',
    'cfn-lint',
    'chardet',
    'click',
    'colorama',
    'coverage',
    'cryptography',
    'cycler',
    'dataclasses',
    'decorator',
    'distlib',
    'dnspython',
    'docker',
    'docutils',
    'dparse',
    'ecdsa',
    'fastapi',
    'filelock',
    'future',
    'greenlet',
    'gunicorn',
    'h11',
    'html5lib',
    'httpie',
    'httpretty',
    'hypothesis',
    'idna',
    'inflect',
    'iniconfig',
    'importlib-metadata',
    'importlib-resources',
    'ipykernel',
    'ipython',
    'ipython-genutils',
    'jedi',
    'jinja2',
    'jmespath',
    'jsondiff',
    'jsonpatch',
    'jsonpointer',
    'jsonschema',
    'junit-xml',
    'jupyter-client',
    'jupyter-console',
    'jupyter-core',
    'kiwisolver',
    'lockfile',
    'mangum',
    'markupsafe',
    'matplotlib',
    'matplotlib-inline',
    'mock',
    'more-itertools',
    'moto',
    'msgpack',
    'networkx',
    'nose',
    'orjson',
    'packaging',
    'parso',
    'pathlib2',
    'pexpect',
    'pickleshare',
    'pillow',
    'pip',
    'pip-api',
    'pip-audit',
    'pluggy',
    'progress',
    'prompt-toolkit',
    'ptyprocess',
    'py',
    'pyasn1',
    'pycparser',
    'pygments',
    'pymongo',
    'pymssql',
    'pyopenssl',
    'pyparsing',
    'pyrsistent',
    'pysocks',
    'pytest',
    'pytest-datadir',
    'python-dateutil',
    'python-jose',
    'pytz',
    'pywin32',
    'pyyaml',
    'pyzmq',
    'requests',
    'requests-toolbelt',
    'resolvelib',
    'responses',
    'rsa',
    's3fs',
    's3transfer',
    'safety',
    'scipy',
    'setuptools',
    'shellingham',
    'simplejson',
    'six',
    'sniffio',
    'sqlalchemy',
    'sshpubkeys',
    'starlette',
    'toml',
    'tornado',
    'tox',
    'traitlets',
    'typer',
    'typing-extensions',
    'urllib3',
    'uvicorn',
    'virtualenv',
    'wcwidth',
    'webencodings',
    'websocket-client',
    'werkzeug',
    'wrapt',
    'xmltodict',
    'zipp',
}

custom_packages = set(os.listdir('packages'))

for custom_package in custom_packages:
    packages.add(custom_package)

with open('index.html.template', 'r') as index:
    index_soup = BeautifulSoup(index, features='html.parser')

outdir = './.publish'
os.makedirs(outdir, exist_ok=True)
os.makedirs('./.vulns', exist_ok=True)

ZipFile(BytesIO(requests.get('https://osv-vulnerabilities.storage.googleapis.com/PyPI/all.zip').content)).extractall('./.vulns/')
vulns = {}

for advisory_file in glob(f'./.vulns/*.json', recursive=True):
    with open(advisory_file, 'r+') as f:
        advisory = json.load(f)
        
        for package in advisory.get('affected', []):
            name = package['package']['name']
            
            if 'versions' in package:
                if name not in vulns:
                    vulns[name] = set(package['versions'])
                else:
                    vulns[name] = vulns[name].union(set(package['versions']))

for package in sorted(packages):
    os.makedirs(f'{outdir}/{package}', exist_ok=True)
    index_entry = index_soup.find(name='a', string=package)

    if not index_entry:
        if package not in custom_packages:
            pypi_url = f'https://pypi.org/simple/{package}/'
            response = requests.get(pypi_url)

            if response.ok:
                pypi_html = requests.get(pypi_url).content
                soup = BeautifulSoup(pypi_html, features='html.parser')
                soup.insert(1, Comment(\
                    f'This file is replicated from {pypi_url}. Do not update directly as updates will be overwritten when the page is updated on PyPi.'))

                with open(f'{outdir}/{package}/index.html', 'w+') as package_index:
                    package_index.write(str(soup))
            else:
                print(f'package {package} could not be found on pypi.org')
                continue
        else:
            shutil.copytree(f'packages/{package}/', f'{outdir}/{package}/', dirs_exist_ok=True)

        if package in vulns:
            with open(f'{outdir}/{package}/index.html', 'r') as f:
                soup = BeautifulSoup(f.read(), features='html.parser')

            for link in soup.find_all('a'):
                name = link.string
                version = None

                if name.endswith('.tar.gz') or name.endswith('.zip'):
                    try:
                        package_name, version = parse_sdist_filename(name)
                    except:
                        #print(f'removing: {link}')
                        link.extract()
                elif name.endswith('.whl'):
                    try:
                        package_name, version, _, _ = parse_wheel_filename(name)
                    except:
                        #print(f'removing: {link}')
                        link.extract()
                else:
                    #print(f'removing: {link}')
                    link.extract()

                if version and version.public in vulns[package]:
                    if package == 'pyyaml':
                        print(f'removing vulnerable version: {link}')
                    link.extract()

            with open(f'{outdir}/{package}/index.html', 'w+') as package_index:
                package_index.write(str(soup))

    index_entry = index_soup.new_tag('a', href=f'/pypi-repo/{package}/')
    index_entry.string = package
    index_entry.append(index_soup.new_tag('br'))
    index_soup.html.body.append(index_entry)
    index_soup.html.body.append('\n')

with open(f'{outdir}/index.html', 'w+') as index_html:
    index_html.write(str(index_soup))

for directory in os.listdir(f'{outdir}'):
    if os.path.isdir(f'{outdir}/{directory}'):
        if directory not in packages and directory not in ['.git', '.github']:
            print(f'Removing {outdir}/{directory}/')
            shutil.rmtree(f'{outdir}/{directory}')

