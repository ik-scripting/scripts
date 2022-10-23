# Attach|Detach Security group to Instance in ASG

Simplify instance management

## Getting started

```sh
pip install pipenv
cd cli-asg-sg && pipenv shell
pipenv sync
./main.py --help
# cleanup venv
rm -rf $(pipenv --venv)
pipenv --rm
# show dependencies
pipenv graph
```

## Commands

The cli read configuration from [this](./config.yaml) file

## Attach/Detach Security Group from instances in ASG

```sh
./main.py --attach
./main.py --detach
```

