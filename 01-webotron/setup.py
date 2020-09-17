from setuptools import setup

setup(
    name='webotron-koro',
    version='0.1',
    author='Marek Korpacz based on Robin Norwood',
    author_email='korobass@o2.pl',
    description='Webetron is a tool to deploy static website on S3, and provide custom domain using CDN',
    license='GPLv3+',
    packages=['webotron'],
    url='https://github.com/korobass/myPython',
    install_requires=[
        'boto3',
        'click'
    ],
    entry_points='''
        [console_scripts]
        webotron=webotron.webotron:cli
    '''
)