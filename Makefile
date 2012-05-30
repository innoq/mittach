.PHONY: init server db terminate release dist deploy test lint coverage clean instance env

init: env instance
	@echo
	@echo "[INFO] use \`source activate\` to activate Python environment"

server: terminate db
	./server & echo $$! > .web.pid

db:
	redis-server > ./redis.log & echo $$! > .db.pid

terminate:
	pkill -TERM -P `cat .web.pid` || true
	kill -TERM `cat .db.pid` || true
	rm .web.pid .db.pid || true

release: dist
	git tag v`python -c 'import mittach; print mittach.__version__'`
	git push

dist: clean test
	rm -r dist || true
	python setup.py sdist

deploy: dist
	./deploy

test: clean terminate db
	py.test -s --tb=short test

lint:
	find . -name "*.py" -not -path "./venv/*" | while read filepath; do \
		pep8 --ignore=E261 $$filepath; \
		pyflakes $$filepath; \
		pylint --reports=n --include-ids=y $$filepath; \
	done

coverage: clean
	# option #1: figleaf
	find mittach test -name "*.py" > coverage.lst
	figleaf `which py.test` test
	figleaf2html -f coverage.lst
	# option #2: coverage
	coverage run `which py.test` test
	coverage html
	# reports
	coverage report
	@echo "[INFO] additional reports in \`html/index.html\` (figleaf) and" \
			"\`htmlcov/index.html\` (coverage)"

clean:
	find . -name "*.pyc" | xargs rm || true
	rm -r mittach.egg-info || true
	rm -rf html .figleaf coverage.lst # figleaf
	rm -rf htmlcov .coverage # coverage
	rm -rf test/__pycache__ # pytest

instance:
	$$SHELL -c '. venv/bin/activate; python -m mittach.instancer instance development'

env:
	virtualenv --distribute venv
	ln -s venv/bin/activate
	$$SHELL -c '. venv/bin/activate; pip install -r REQUIREMENTS.txt' # XXX: `REQUIREMENTS.txt` should be replaced by dependency info from `setup.py`
