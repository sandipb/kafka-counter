from distutils.core import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='kafka-counter',
    version='0.0.1',
    description="Kafka message counter",
    url='https://github.com/sandipb/kafka-counter',
    author='Sandip Bhattacharya',
    author_email="pypi@r.sandipb.net",
    long_description=readme(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Topic :: Utilities",
    ],
    keywords=["kafka"],
    entry_points={
        'console_scripts': ['kafka-count=kafka_count:main']
    },
    license='Apache 2.0',
    include_package_data=True,
    install_requires=[
        'pyaml',
        'jsonpath-ng',
        'kafka-python',
        'python-snappy',
    ]
)