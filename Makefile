.DEFAULT_GOAL := help

pico-sync:  ## Sync the CircuitPython code onto the pico
	@cp -r pico/* $$(mount | grep CIRCUITPY | cut -d' ' -f 3)

mixer:  ## Start the sound mixer
	@poetry run python pico_mixer/mixer.py

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
