# belief-state-machine

See [prompts design file](path/to/prompts_system_design_file.md) for the philosophy behind this.

This app extracts beliefs from a text and context, and generates stories out of a mix of context and beliefs which operate on the extracted beliefs. The operations on the beliefs are to reinforce the belief, change the belief, or render the belief meaningless.


## Architecture

AWS ECS cluster with 2 services:
- frontend: static files and React app
- backend: Django app

`make scale-up` and `make scale-down` to spin up/down the ECS services, since this is a demo that doesn't need to be on 24/7.
