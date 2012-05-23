.PHONY: init server db terminate dist test lint coverage clean secret env

init: env secret
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

dist: clean test
	python setup.py sdist

test: clean
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

secret:
	$$SHELL -c 'echo $$RANDOM | sha1sum > secret' # XXX: suboptimal

env:
	virtualenv --no-site-packages venv
	ln -s venv/bin/activate
	$$SHELL -c '. venv/bin/activate; pip install -r REQUIREMENTS.txt'
