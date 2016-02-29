import asyncio
import fcntl
import gc
import docker
import pytest
import socket
import struct
import uuid


def get_ip_address(ifname):
    """
    Returns IP address of the given interface name.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15].encode('utf-8'))
    )[20:24])


@pytest.fixture(scope='session')
def unused_port():
    def factory():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 0))
            return s.getsockname()[1]
    return factory


@pytest.fixture(scope='session')
def session_id():
    return str(uuid.uuid4())


@pytest.yield_fixture(scope='session')
def kafka_server(unused_port, session_id):
    image_name = 'pygo/kafka:2.11_0.9.0.1'
    docker_client = docker.Client(version='auto')
    docker_client.pull(image_name)
    kafka_host = get_ip_address('docker0')
    kafka_port = unused_port()
    container = docker_client.create_container(
        image=image_name,
        name='aiokafka-tests-{}'.format(session_id),
        ports=[2181, 9092],
        environment={
            'ADVERTISED_HOST': kafka_host,
            'ADVERTISED_PORT': kafka_port,
            'NUM_PARTITIONS': 2
        },
        host_config=docker_client.create_host_config(
            port_bindings={
                2181: (kafka_host, unused_port()),
                9092: (kafka_host, kafka_port)
            }))
    docker_client.start(container=container['Id'])
    yield kafka_host, kafka_port
    docker_client.kill(container=container['Id'])
    docker_client.remove_container(container['Id'])


@pytest.yield_fixture(scope='class')
def loop(request):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

    yield loop

    if not loop._closed:
        loop.call_soon(loop.stop)
        loop.run_forever()
        loop.close()
    gc.collect()
    asyncio.set_event_loop(None)


@pytest.fixture(scope='class')
def setup_test_class(request, loop):
    request.cls.loop = loop
