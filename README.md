# arbor-dominii
Tool for making possession trees

## launch 

### Docker compose (recommended)

```docker compose up```

### Docker

```docker build . -t ad
docker run --name ad --mount type=bind,src="$(pwd)",target=/harbour/environment ad```
