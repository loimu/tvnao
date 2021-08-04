from setuptools import setup

setup(
    name='tvnao',
    version='0.12.0',
    description='watch tv here and now (nao)',
    long_description='a tool for watching IP TV, shows TV guide',
    author='blaze',
    author_email='blaze@vivaldi.net',
    url='https://github.com/loimu/tvnao',
    packages=['tvnao'],
    keywords='iptv, jtv, guide, m3u, mpv, qt',
    license="GPL-3",
    entry_points={
        'gui_scripts': ['tvnao = tvnao.tvnao:main']
    },
    data_files = [
        ('share/applications', ['data/tvnao.desktop']),
    ],
)
