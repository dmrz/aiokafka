import docker as libdocker
import pytest
import socket
import uuid


@pytest.fixture
def unused_port():
    def factory():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 0))
            return s.getsockname()[1]
    return factory


@pytest.fixture(scope='session')
def session_id():
    return str(uuid.uuid4())


@pytest.fixture(scope='session')
def docker():
    return libdocker.Client(version='auto')


@pytest.yield_fixture(scope='session')
def kafka_server(unused_port, session_id, docker):
    image_name = 'pygo/kafka:2.11_0.9.0.1'
    docker.pull(image_name)
    kafka_port = unused_port()
    container = docker.create_container(
        image=image_name,
        name='test-kafka-{}'.format(session_id),
        ports=[2181, 9092],
        host_config=docker.create_host_config(
            port_bindings={2181: unused_port(), 9092: kafka_port}))
    docker.start(container=container['Id'])
    yield kafka_port
    docker.kill(container=container['Id'])
    docker.remove_container(container['Id'])


# @pytest.fixture
# def kafka_client(kafka_server):
#     pass
