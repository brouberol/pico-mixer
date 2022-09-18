.DEFAULT_GOAL := help

pico-sync:  ## Sync the CircuitPython code onto the pico
	@cp -r pico/* $$(mount | grep CIRCUITPY | cut -d' ' -f 3)

mixer:  ## Start the sound mixer terminal application
	@poetry run python pico_mixer/mixer.py

webmixer:  ## Start the web-based sound mixer
	@cd pico_mixer_web && poetry run python server.py

install:  ## Install python dependencies
	poetry install
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
