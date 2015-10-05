from setuptools import setup

setup(name='aal',
      version='0.2',
      description='album art learner',
      long_description="""
      learns your top last.fm albums and 
      lets you perform an image search
      to test if that album is in your database
      """,
      url='http://github.com/pussinboot/aal',
      packages=['aal'],
      install_requires=[
      	"Pillow",
      	"numpy",
      	"scikit-image",
      	"scikit-learn"
      ],
       package_data={
        'aal' : ['test.png']
    	},
       entry_points = {
            'console_scripts': [
                'aal = aal.aal:main'
            ]
        })