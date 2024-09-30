from click.testing import CliRunner
from tlparser.cli import cli
import os
import shutil

# Constants for paths
TEST_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
WORKING_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "tlparser", "workingdir")
)


def test_digest_command():
    runner = CliRunner()

    print(f"***TEST_DATAD_DIR: {TEST_DATA_DIR}")
    print(f"***WORKING_DIR: {WORKING_DIR}")

    # Path to test input JSON
    test_json = os.path.join(TEST_DATA_DIR, "test.json")

    # Ensure the working directory exists
    os.makedirs(WORKING_DIR, exist_ok=True)

    # List files in the working directory before running digest
    files_before = set(os.listdir(WORKING_DIR))

    with runner.isolated_filesystem():
        # Invoke the digest command
        result = runner.invoke(cli, ["digest", test_json])

        # Check for correct exit code
        assert result.exit_code == 0

    # List files in the working directory after running digest
    files_after = set(os.listdir(WORKING_DIR))
    print(f"***files_after: {files_after}")

    # Identify the newly created file(s)
    new_files = files_after - files_before
    assert len(new_files) == 1, "Expected exactly one new file, but found: {}".format(
        new_files
    )

    # Get the path to the new file
    new_file_path = os.path.join(WORKING_DIR, new_files.pop())

    # Verify that the new file exists
    assert os.path.isfile(new_file_path), f"Output file {new_file_path} does not exist."

    # Additional checks to verify content or format of the output file
    # For example, if it's an Excel file, you could read it using pandas:
    import pandas as pd

    df = pd.read_excel(new_file_path)

    # Assert that the dataframe is not empty
    assert not df.empty, "The output file is empty."


def teardown_module():
    if os.path.isdir(WORKING_DIR):
        shutil.rmtree(WORKING_DIR)
