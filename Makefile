PYTHON ?= python3
VENV := .venv
BIN := $(VENV)/bin

export GITHUB_TOKEN ?= $(shell gh auth token 2>/dev/null)

.PHONY: build serve post clean strava-auth linkedin-auth

$(BIN)/python: requirements.txt
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install -q -r requirements.txt
	@touch $@

build: $(BIN)/python
	$(BIN)/python build.py

serve: $(BIN)/python
	$(BIN)/python build.py serve

# make post title="My new post"
post:
	@test -n "$(title)" || (echo 'usage: make post title="My new post"' && exit 1)
	@slug=$$(echo "$(title)" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-|-$$//g'); \
	mkdir -p content/posts; file=content/posts/$$slug.md; \
	test ! -e $$file || (echo "$$file already exists" && exit 1); \
	printf -- '---\ntitle: "%s"\ndate: %s\ndescription: ""\ntags: []\ndraft: true\n---\n\n' "$(title)" "$$(date +%Y-%m-%dT%H:%M:%S%z | sed -E 's/([0-9]{2})([0-9]{2})$$/\1:\2/')" > $$file; \
	echo "created $$file"

strava-auth:
	$(PYTHON) auth.py strava

linkedin-auth:
	$(PYTHON) auth.py linkedin

clean:
	rm -rf public .cache
