# arbor-dominii
Tool for making possession trees

## launch 

### Docker compose (recommended)

```shell
docker compose up
```

### Docker

```shell
docker buildx build . -t ad
docker run --name ad --mount type=bind,src="$(pwd)",target=/harbour/environment ad
```
