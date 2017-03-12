from setuptools import setup

setup(name='musicnow',
      version='5.0',
      description='Lets you download music with album art and metadata',
      url='https://github.com/lakshaykalbhor/MusicNow',
      author='Lakshay Kalbhor',
      author_email='lakshaykalbhor@gmail.com',
      license='MIT',
      packages =['musicnow'],
      install_requires=[
          'youtube-dl',
          'bs4',
          'mutagen',
          'requests',
          'spotipy',
          'six',
          'colorama',
          'argparse',
          'configparser',
        ],
      entry_points={
        'console_scripts': ['musicnow=musicnow.command_line:main'],
      },
      package_data={'musicnow':['config.ini']},
      )
