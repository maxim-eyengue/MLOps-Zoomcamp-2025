## Deploying a model as a web-service
Note that we created a virtual environment with `Pipenv` and a [python script](./predict.py) for making predictions. The sript was put the into a `Flask` app and everything was then packaged using a [dockerfile](./Dockerfile).

To build the docker image:
```bash
docker build -t ride-duration-prediction-service:v1 .
```
- `-t`: specifies the image name (zoomcamp-test in this case).
- `.`: indicates that the [Dockerfile](./Dockerfile) in the current directory should be used.

To run the image:
```bash
docker run -it --rm -p 9696:9696  ride-duration-prediction-service:v1
```
- `-it`: to run the container in an interactive mode so to get access to the container's terminal for example, or be able to exit it with Ctrl+C.
- `--rm`: to remove the image after the session ends.
- `-p`: to map the port on the host machine to the port on the Docker container.

To make predictions using the test script:
```sh
python test.py
```