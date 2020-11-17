import os
import sys
from pathlib import Path

from azure.storage.blob import BlobServiceClient
import click
from tqdm import tqdm


class ProgressStream():

    def __init__(self, stream, pbar):
        self._pbar = pbar
        self._stream = stream

    def read(self, *args, **kwargs):
        result = self._stream.read(*args, **kwargs)
        self._pbar.update(len(result))
        return result

    def write(self, *args, **kwargs):
        result = self._stream.write(*args, **kwargs)
        self._pbar.update(result)
        return result

    def __getattr__(self, attr):
        return getattr(self._stream, attr)

    def __enter__(self, *args, **kwargs):
        self._stream.__enter__(*args, **kwargs)
        return self

    def __exit__(self, *args, **kwargs):
        self._stream.__exit__(type, *args, **kwargs)


@click.command()
@click.option('--force', '-f', is_flag=True, default=False)
@click.argument('source')
@click.argument('target')
def main(force, source, target):

    connection_str = os.getenv('AZURE_CONNECTION_STRING')
    if connection_str is None:
        print("Set the AZURE_CONNECTION_STRING environment variable", file=sys.stderr)
        sys.exit(1)

    client = BlobServiceClient.from_connection_string(connection_str)

    try:
        container_name, source = source.split(':')
        download = True
    except ValueError:
        try:
            container_name, target = target.split(':')
            download = False
        except ValueError:
            print("Either SOURCE or TARGET must be on the form 'container:path'", file=sys.stderr)
            sys.exit(2)

    blob_name = source if download else target
    file_name = Path(target if download else source)

    container = client.get_container_client(container_name)
    blob = container.get_blob_client(blob_name)

    if blob.exists() and not download:
        if force:
            blob.delete_blob()
        else:
            print(f"{container_name}:{blob_name} already exists, use -f to force")
            sys.exit(3)

    if not blob.exists() and download:
        print(f"{container_name}:{blob_name} does not exist")
        sys.exit(4)

    if not download and not file_name.is_file():
        print(f"{file_name} does not exist or is not a file")

    if download:
        progressbar = tqdm(total=blob.get_blob_properties()['size'], unit='B', unit_scale=True, unit_divisor=1024)
        with ProgressStream(open(file_name, 'wb'), progressbar) as f:
            blob.download_blob().readinto(f)
    else:
        progressbar = tqdm(total=file_name.stat().st_size, unit='B', unit_scale=True, unit_divisor=1024)
        with ProgressStream(open(file_name, 'rb'), progressbar) as f:
            blob.upload_blob(f)
