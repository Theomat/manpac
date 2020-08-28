# manpac


## Description

pac-man but it's reversed, pac-man is eating the ghosts and the ghosts have to survive.
The objective of a ghost is to be the last one alive.

pac-man has a simple AI where he will move towards the closest ghost.
He is also a bit faster than the ghosts, and the ghosts can't block each other.

The twist ?
There are power-ups that will spawn on the map, only the ghosts can pick them up and they grant bonuses for a short duration or instantaneous effects upon activation.
These power-ups if not picked up will disappear after some time.
Once a power-up is picked up or disappear, a pac-man power-up spawns at the same location, which dramatically boosts pac-man for a short duration. Of course, only pac-man can pick it up.

## Writing code

- *Commits, Code, Documentation* in **English**.
- Make *small* **changes** in each commit.
- Use **snake case** (like_this not likeThis) for everything except class names.
- Use **camel case** (likeThis not like_this) for class names.
- Format code using [autopep8](https://github.com/hhatto/autopep8), [atom package](https://atom.io/packages/python-autopep8)


## Dependencies

- python >= 3.6
- [numpy](https://numpy.org/)
- [pygame](https://www.pygame.org/)
- [pytest](https://github.com/pytest-dev/pytest/)

You can easily create an environment with the right dependencies:
```bash
conda create --name manpac python>=3.6 numpy pygame pytest
```

## Branches

- ```master``` is the stable branch
- ```dev``` is the development branch


## Tests

They can be run with :
```bash
python -m pytest
```
