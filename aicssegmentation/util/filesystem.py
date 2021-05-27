from pathlib import Path


class FileSystemUtilities:
    @staticmethod
    def create_directory(path: str):
        """
        Create directory for the given path. This will create all parent directories as needed.
        """
        Path(path).mkdir(exist_ok=True, parents=True)
