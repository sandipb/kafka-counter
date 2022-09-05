.PHONY: build clean upload uploadtest upload

build:
	python3 -m build

clean:
	rm dist/*

uploadtest:
	twine upload --repository testpypi dist/*

upload:
	twine upload dist/*