# arbor-dominii
Tool for making possession trees

## launch 

### Docker compose (recommended)

```shell
docker compose up
```

### Docker

```shell
docker buildx build . -t arbor-dominii
docker run --name arbor-dominii --mount type=bind,src="$(pwd)",target=/harbour/environment arbor-dominii
```

### persistent mode (development)

```shell
docker buildx build . -f Dockerfile_persistent -t arbor-dominii-persistent
docker run -dt --name arbor-dominii-persistent --mount type=bind,src="$(pwd)",target=/harbour/environment arbor-dominii-persistent
```

then you can enter "arbor-dominii-persistent" container, open the harbour folder and launch main.py using

```shell
python3 main.py
```
