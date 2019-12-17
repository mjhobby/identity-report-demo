from setuptools import setup


setup(
    name="identity-report-demo",
    author="M Jacob Hobby",
    author_email="mjhobby@umich.edu",
    version="0.0.1",
    entry_points={
        'console_scripts': [
            'identity_report = identity_report.scripts.run:main',
        ]
    },
    zip_safe=True,
)
